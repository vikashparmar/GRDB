from mysql.connector import Error, connect, errorcode
import time
import datetime
from framework.AppConfig import AppConfig
from framework.formats.objects.Strings import Strings
from framework.system.LogService import LogService
from framework.formats.objects.DictProcessor import DictProcessor
from framework.formats.objects.DictArrays import DictArrays
from framework.formats.objects.Strings import Strings
from functools import lru_cache
from framework.system.sql.SQLRowRecord import SQLRowRecord
from framework.system.sql.SQLRecordType import SQLRecordType
from framework.system.sql.SQLTableRecord import SQLTableRecord


class DatabaseService():
	table_records:dict

	def record_sql_queries(self, table_name=None, values=None, record_type=None, multiple=False, current_row_id=0, where_clauses=[]):
		if AppConfig.LOCAL_TESTING and AppConfig.LOCAL_RECORD_QUERIES:
			if not table_name in self.table_records:
				table_record = SQLTableRecord()
				table_record.tableName = table_name
				self.table_records[table_name] = table_record

			values = DictArrays.fillValues(values, multiple)

			# To add the action column
			if record_type == SQLRecordType.INSERT_ROW:
				action = "Insert"
			elif record_type == SQLRecordType.UPDATE_ROW:
				action = "Update"
			elif record_type in [SQLRecordType.DELETE_ROW, SQLRecordType.DELETE_ROWS, SQLRecordType.DELETE_ALL_ROWS]:
				action = "Delete"
				
			# For the case of INSERT
			if record_type == SQLRecordType.INSERT_ROW:
				if multiple:
					for value in values:
						row_record = SQLRowRecord()
						row_record.tableName = table_name
						row_record.recordType = record_type
						value.update({"Action" : action})
						row_record.rowData = value
						self.table_records[table_name].rows.append(row_record)
				else:
					row_record = SQLRowRecord()
					row_record.tableName = table_name
					row_record.recordType = record_type
					values.update({"Action" : action})
					row_record.rowData = values
					row_record.rowID = current_row_id
					self.table_records[table_name].rows.append(row_record)

			# In Case delete all rows
			elif record_type == SQLRecordType.DELETE_ALL_ROWS:
				row_record = SQLRowRecord()
				row_record.tableName = table_name
				row_record.recordType = record_type
				self.table_records[table_name].rows.append(row_record)

			# For the case of UPDATE / DELETE
			else:
				for clause in where_clauses:
					row_record = SQLRowRecord()
					row_record.tableName = table_name
					row_record.recordType = record_type
					values.update({"Action" : action})
					row_record.rowData = values
					row_record.whereData = clause
					self.table_records[table_name].rows.append(row_record)


	@staticmethod
	def connect_retry_loop(retries, host, port, database, user, password):

		conn = None
		
		# retry 15 times x 2 seconds so retries for 30 seconds
		for retry in range(1,retries):
			try:

				# try to acquire a database connection
				conn = DatabaseService(host, port, database, user, password)

				# break retry-loop if connection was made
				if conn is not None:
					return conn
				
			except Exception as e:

				# log error and retry
				LogService.error(f"Error connecting to MySQL DB! Attempt: {retry}", e)
				conn = None
			
			# pause 2 seconds
			time.sleep(2)

		# if unable to connect to DB, log error and fail app
		if conn is None:
			LogService.error("Exhausted all attempts to connect to MySQL DB!")

			return None
		

	@staticmethod
	def connect(host, port, database, user, password):
		return DatabaseService(host, port, database, user, password)


	def __init__(self, host, port, database, user, password):
		self.host = host
		self.port = port
		self.database = database
		self.user = user
		self.password = password
		self.db_read_count = 0
		self.db_write_count = 0
		self.__connect()
		self.__batch_reset()
		self.table_records = {}


	def __connect(self):

		# create the main read/write connection
		self.conn = connect(host=self.host, database=self.database, user=self.user, password=self.password, port=self.port)
		if self.conn.is_connected():
			LogService.log('Connected to MySQL database!')
			LogService.log(f'Connected to Host: {self.host}, Database: {self.database}')

		# return ref to new connection
		return self.conn


	# Reconnect any given connection and return a ref to the new connection
	def __reconnect(self, conn):

		# if its the batch connection, reconnect it
		if self.batch_enabled == True and conn == self.batch_conn:
			return self.__batch_connect()
		else:

			# in most cases just reconnect the main R/W connection
			return self.__connect()


	def dispose(self):
		try:

			# close the batch transaction
			self.batch_end()

			# close the main read/write connection
			if self.conn is not None:
				self.conn.close()
				self.conn = None

			# close batch write connection
			if self.batch_conn is not None:
				self.batch_conn.close()
				self.batch_conn = None

		except Exception as e:

			# absorb error but report it
			LogService.error('Failed to Dispose MySQL', e)


	# returns the main read connection. never returns None.
	def __get_main_connection(self):
		if self.conn.is_connected():
			return self.conn
		else:
			self.__connect()


	# returns the main batch writing connection. never returns None.
	def __get_write_connection(self):
		if AppConfig.BATCH_WRITES:
			if self.batch_conn is None:
				self.__batch_connect()

			# if batching is active, use the write connection
			if self.batch_enabled == True and self.batch_conn is not None:
				return self.batch_conn

		# if batching is disabled or not active, use the main connection	
		return self.conn


	# returns the read connection or the batch writing connection, depending on the query. never returns None.
	def __get_any_connection(self, query):
		queryLower = query.strip().lower()

		# if its a select query, do it on the main connection
		if queryLower.startswith('select'):
			return self.conn

		# if its a query with blocked tables, do it on the main connection
		elif self.__is_blocked_table(queryLower):
			return self.conn

		# if its a write query, do it on the batch connection
		# and as a fallback return the main connection
		return self.__get_write_connection()


	# Must occur ONLY when the DB class is first created, never again
	def __batch_reset(self):
		self.batch_conn = None
		self.batch_enabled = False
		self.batch_open_trans = False
		self.batch_count = 0


	# Open a new batch connection if it is not already open.
	# Always tries to create a new connection.
	# Returns the new connection, or returns None if failed to make one.
	def __batch_connect(self):

		# create a new connection for batch writes
		try:
			self.batch_conn = connect(host=self.host, database=self.database, user=self.user, password=self.password)
		except Exception as e:
			LogService.error('Batch: Failed to connect to MySQL database', e)

		# if it got connected
		if self.batch_conn is not None and self.batch_conn.is_connected():
			LogService.log('Batch: Connected to MySQL database!')
			LogService.log(f'Batch: Connected to Host: {self.host}, Database: {self.database}')
			LogService.log('Batch: Enabled')
			
			# reset batching status
			self.batch_enabled = True
			self.batch_open_trans = False
			self.batch_count = 0

		# if failed to make a new connection
		else:

			# simply use the main connection from now on
			LogService.log('Batch: Disabled')
			self.batch_enabled = False
			self.batch_conn = None

		# return ref to new connection or None
		return self.batch_conn


	# Open a new batch transaction if it is not already open. Only works if the batch connection is open and ready.
	def __batch_begin(self):

		# only if we are in batch mode
		if self.batch_enabled == True and self.batch_conn is not None:

			# only if there is a CLOSED transaction
			if self.batch_open_trans == False:

				# change status
				LogService.log(f"Batch: Started new batch")
				self.batch_open_trans = True
				self.batch_count = 0

				# begin the transaction
				#self.__execute_batch("BEGIN TRANSACTION")

				# open a new cursor
				self.batch_cursor = self.batch_conn.cursor(buffered=True)



	# Close up the batch transaction if any is open. Only works if the batch connection is open and ready.
	# Public API because you can call this to close the batch transaction and commit to DB.
	def batch_end(self):

		# only if we are in batch mode
		if self.batch_enabled == True and self.batch_conn is not None:

			# only if there is an OPEN transaction
			if self.batch_open_trans == True:

				# change status
				LogService.log(f"Batch: Ended batch with {str(self.batch_count)} queries")
				self.batch_open_trans = False

				# commit the transaction
				#self.__execute_batch("COMMIT TRANSACTION")

				# commit the transaction and close the cursor
				self.batch_conn.commit()
				self.batch_cursor.close()
				self.batch_cursor = None




	# Open a transaction if its not already open. Only works if the batch connection is open and ready.
	def __batch_before_query(self):
		self.__batch_begin()


	# Close the transaction if we have reached the configured pack size
	def __batch_after_query(self):

		# only if we are in batch mode
		if self.batch_enabled == True and self.batch_conn is not None:

			# only if there is an OPEN transaction
			if self.batch_open_trans == True:

				# increment the count of writes done in this transaction
				self.batch_count = self.batch_count + 1

				# close the transaction if we have reached the configured pack size
				if self.batch_count >= AppConfig.BATCH_PACK_SIZE:
					self.batch_end()
					self.batch_count = 0


	# Immediately execute a query on the batch write connection
	def __execute_batch(self, query):

		# query metrics
		self.__count_query(query)

		# use write connection only
		conn = self.__get_write_connection()
		if conn == self.batch_conn:
			
			# create a new cursor that automatically gets disposed as per best practices
			with conn.cursor(buffered=True) as cursor:
				try:
					LogService.log(f"Batch: Instantly executed: {query}")
					cursor.execute(query)
					conn.commit()
					return True
				except Exception as e:

					# retry if DB connection was lost and its reconnected now
					if self.__retry_command(conn, e):
						return self.__execute_batch(query)

					# abort with error
					LogService.error('MySQL Error running batch query: ' + query, e)
					return True
		else:
			# skipped because unable to open write connection
			return False




	# should this command be retried because the error was due to DB connection lost?
	def __retry_command(self, conn, e):

		# check for 2006: MySQL server has gone away
		# check for 2055: Lost connection to MySQL server at 'grdb.c2brhzmmmjb5.us-east-2.rds.amazonaws.com:3306', system error: 10060 A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond
		# check for 2013: Lost connection to MySQL server during query
		if hasattr(e, 'errno') and e.errno in [errorcode.CR_SERVER_GONE_ERROR, errorcode.CR_SERVER_LOST_EXTENDED, errorcode.CR_SERVER_LOST]:
			
			# try reconnecting once
			try:
				conn = self.__reconnect(conn)
				if conn.is_connected():
					LogService.log('MySQL: Automatically reconnected after database connection lost!')

					# return true so the parent function retries its SQL command
					return True

			except Exception as e2:
				LogService.error('MySQL Error: Database connection lost and failed to reconnect to MySQL database', e2)
				
		# return false meaning the error must be handled another way
		return False


	# check if the query is modifying a blocked table
	# WGP-601: Support blocked tables so job table not modified during local testing
	def __is_blocked_table(self, queryLower):
		if AppConfig.LOCAL_BLOCKED_TABLES is not None and len(AppConfig.LOCAL_BLOCKED_TABLES) > 0:
			for blocked in AppConfig.LOCAL_BLOCKED_TABLES:
				blocked_lower = blocked.lower()
				if queryLower.startswith(('insert into ' + blocked_lower, 'update ' + blocked_lower, 'delete from ' + blocked_lower)):
					return True
		return False


			
	def __can_execute_query(self, query):

		# when running on the cloud, always execute all queries
		if not AppConfig.LOCAL_TESTING:
			return True

		# when performing local testing, check the query
		if AppConfig.LOCAL_TESTING:

			queryLower = query.strip().lower()

			# if its a select query, allow it
			if queryLower.startswith('select'):
				return True

			# if its trying to edit blocked tables, reject it always
			if self.__is_blocked_table(queryLower):
				return False

			# if its trying to edit other tables, only allow if configured to do so
			if queryLower.startswith(('insert', 'update', 'delete')):
				if AppConfig.LOCAL_MODIFY_DB:
					return True

		# if unknown, do not execute the query
		return False


		
	# Only for SELECT queries
	def select_all_safe(self, query, values, rowDict=False, replaceMap=None):
		try:

			# query metrics
			self.__count_query(query)

			# get final query based on the replace map
			if replaceMap is not None:
				query = DictProcessor.replaceStrProps(query, replaceMap)

			# use read connection
			conn = self.__get_main_connection()

			# create a new cursor that automatically gets disposed as per best practices
			with conn.cursor(buffered=True, dictionary=rowDict) as cursor:
				cursor.execute(query, values)
				rows = cursor.fetchall()
				conn.commit()

				# replace props based on replace map
				if replaceMap is not None and rows is not None and len(rows) > 0 and rowDict == True:
					return DictArrays.replaceProps(rows, replaceMap, True)

				return rows

		except Exception as e:

			# retry if DB connection was lost and its reconnected now
			if self.__retry_command(conn, e):
				return self.select_all_safe(query, values, rowDict, replaceMap)

			# abort with error
			LogService.error('MySQL Error: ' + query, e)
			raise

	# Only for SELECT queries.
	# Execute a query but cache the response using Least Recently Used (LRU) caching strategy.
	@lru_cache(maxsize=1024)
	def select_all_safe_cached(self, query, values, rowDict=False, replaceMap=None):
		rows = self.select_all_safe(query, values, rowDict, replaceMap)
		return rows


	# Only for SELECT queries
	def select_first(self, tablename, order_by):
		lastrow = None
		try:

			# query metrics
			self.__count_query('SELECT')

			# use read connection
			conn = self.__get_main_connection()

			# create a new cursor that automatically gets disposed as per best practices
			with conn.cursor(buffered=True) as cursor:
				query = f"SELECT {order_by} FROM {tablename} ORDER BY {order_by} DESC LIMIT 1"
				cursor.execute(query)
				lastrow = cursor.fetchone()
				conn.commit()
				return lastrow
			
		except Exception as e:

			# retry if DB connection was lost and its reconnected now
			if self.__retry_command(conn, e):
				return self.select_first(tablename, order_by)

			# abort with error
			if lastrow is None:
				LogService.error('No records found for this query. Query: ' + query + ', Table: ' + tablename + ', Sort: ' + order_by, e)
			else:
				LogService.error('MySQL Error. Query: ' + query + ', Table: ' + tablename + ', Sort: ' + order_by, e)
			raise


	# Only for INSERT queries.
	# Returns the last row ID.
	# Immediately run. Never batched because new row ID is required as return value.
	def _insert_id_safe(self, query, value):
		try:

			# query metrics
			self.__count_query(query)

			# skip executing some queries if local testing
			if not self.__can_execute_query(query):
				#LogService.print(f"Skipped executing: {query}")
				return -1

			# use read connection
			conn = self.__get_main_connection()

			# create a new cursor that automatically gets disposed as per best practices
			with conn.cursor(buffered=True) as cursor:
				if AppConfig.BATCH_WRITES:
					LogService.log('Instant: Insert for row ID: ' + query[0:50] + '...')
				cursor.execute(query, value)
				conn.commit()
				lastrowid = cursor.lastrowid
				return lastrowid
			
		except Exception as e:

			# retry if DB connection was lost and its reconnected now
			if self.__retry_command(conn, e):
				return self._insert_id_safe(query, value)

			# abort with error
			LogService.error('MySQL Error. Query: ' + str(query) + ', Value: ' + str(value), e)
			raise


	# Only for Bulk INSERT, Bulk UPDATE and Bulk DELETE queries.
	# Immediately run. Never batched because not required.
	def _insert_multiple_safe(self, query, datalist):
		try:

			# query metrics
			self.__count_query(query)

			# skip executing some queries if local testing
			if not self.__can_execute_query(query):
				#LogService.print(f"Skipped executing: {query}")
				return
			
			# always use read connection
			conn = self.__get_main_connection()
			
			# create a new cursor that automatically gets disposed as per best practices
			with conn.cursor(buffered=True) as cursor:
				cursor.executemany(query, datalist)
				conn.commit()
				
		except Exception as e:

			# retry if DB connection was lost and its reconnected now
			if self.__retry_command(conn, e):
				return self._insert_multiple_safe(query, datalist)

			# abort with error
			LogService.error('MySQL Error. Query: ' + query + ', Data: ' + str(datalist), e)
			raise


	# Only for INSERT, UPDATE and DELETE queries.
	# Cannot have any return value.
	# Conditionally Batched if it is a write query and batching is enabled for that table.
	# If `value` is passed, then it is SAFE mode as SQL injection is not possible.
	# If `value` is not passed, then it is UNSAFE made as SQL injection is possible.
	def batch_execute(self, query, value=None) -> bool:

		# query metrics
		self.__count_query(query)

		# skip executing some queries if local testing
		if not self.__can_execute_query(query):
			#LogService.print(f"Skipped executing: {query}")
			return False

		# use main or write connection depending on which table
		conn = self.__get_any_connection(query)

		# batch mode
		if conn == self.batch_conn:

			# execute before-query logic
			self.__batch_before_query()

			# execute command on cursor but DONT commit
			try:
				LogService.log("Batch: Recorded query: " + query[0:50] + '...')
				if value is None:
					self.batch_cursor.execute(query)
				else:
					self.batch_cursor.execute(query, value)
			except Exception as e:

				# retry if DB connection was lost and its reconnected now
				if self.__retry_command(conn, e):
					return self.batch_execute(query, value)

				# abort with error
				LogService.error('MySQL Error. Query: ' + str(query) + ', Value: ' + str(value), e)
				raise

			# execute after-query logic
			self.__batch_after_query()
		
		# immediate execution mode
		# create a new cursor that automatically gets disposed as per best practices
		with conn.cursor(buffered=True) as cursor:
			try:

				# execute command
				if value is None:
					cursor.execute(query)
				else:
					cursor.execute(query, value)

				# commit IMMEDIATELY
				conn.commit()
				return True

			except Exception as e:

				# retry if DB connection was lost and its reconnected now
				if self.__retry_command(conn, e):
					return self.batch_execute(query, value)

				# abort with error
				LogService.error('MySQL Error. Query: ' + str(query) + ', Value: ' + str(value), e)
				raise

		return False
	

	def reset_metrics(self):
		self.db_read_count = 0
		self.db_write_count = 0
		
	def __count_query(self, query:str):

		# clean query
		queryLower:str = query.strip().lower()

		#-------------------------------
		# 		QUERY COUNTING
		#-------------------------------

		# if its a select query, count as read
		if queryLower.startswith('select'):
			self.db_read_count += 1

		# if its modificatiton query, count as write
		if queryLower.startswith(('insert', 'update', 'delete')):
			self.db_write_count += 1

		#------------------------------------
		#		QUERY ERROR VALIDATION
		#------------------------------------
		if AppConfig.LOCAL_TESTING:

			# extract query values
			values = None
			if query.startswith('INSERT') and ' VALUES ' in query:
				values = Strings.afterFirst(query, ' VALUES ')
			elif query.startswith('UPDATE') and ' SET ' in query:
				values = Strings.afterFirst(query, ' SET ')

			# ensure no values are "None"
			if values is not None:
				if 'None' in values:
					raise ValueError("Warning: INSERT/UPDATE query has a None value")


		

	def get_metrics(self):
		return self.db_read_count, self.db_write_count


	def _insert_record(self, table, values, multiple, replaceMap=None) -> int:

		# exit if no work
		if values == None or len(values) == 0:
			return -1

		# get final dict based on the replace map
		if replaceMap is not None:
			if multiple:
				values = DictArrays.replaceProps(values, replaceMap)
			else:
				values = DictProcessor.replaceProps(values, replaceMap)

			# get final table name based on the replace map
			if table in replaceMap:
				table = replaceMap[table]

		# use props of first object if multiple objects given
		if multiple:
			loop_obj = values[0]
		else:
			loop_obj = values

		# collect props and values
		props = []
		vals = []
		query_vals = []
		for prop in loop_obj:
			props.append(prop)
			vals.append("%s")
			query_vals.append(loop_obj[prop])

		# collect values for multiple query objects
		if multiple:
			multi_query_vals = []
			for obj in values:

				# collect all values of this object in the same order
				# as the props that were collected from the 1st object
				obj_vals = []
				multi_query_vals.append(obj_vals)
				for prop in props:
					obj_vals.append(obj[prop])

		# create SQL INSERT statement
		parts = ["INSERT INTO ", table, " ("]
		parts.append(",".join(props))
		parts.append(") VALUES (")
		parts.append(",".join(vals))
		parts.append(")")
		query = "".join(parts)

		# execute statement and return new row ID
		if multiple:
			# Recording all query objects
			return_value = self._insert_multiple_safe(query, multi_query_vals)
			self.record_sql_queries(table, values, SQLRecordType.INSERT_ROW, multiple)
			return return_value
		else:
			# Recording all query objects
			current_row_id = self._insert_id_safe(query, query_vals)
			self.record_sql_queries(table, values, SQLRecordType.INSERT_ROW, multiple, current_row_id)
			return current_row_id


	def insert_record(self, table, values, replaceMap=None) -> int:
		return self._insert_record(table, values, False, replaceMap)

	def insert_records(self, table, values, replaceMap=None) -> int:
		return self._insert_record(table, values, True, replaceMap)



	def update_record(self, table, id_col, row_id, values, replaceMap=None) -> bool:

		# exit if no work
		if values == None or len(values) == 0:
			return -1

		# if find and replace needed
		if replaceMap is not None:

			# get final dict based on the replace map
			values = DictProcessor.replaceProps(values, replaceMap)

			# get final table name based on the replace map
			if table in replaceMap:
				table = replaceMap[table]

			# get final col name based on the replace map
			if id_col in replaceMap:
				id_col = replaceMap[id_col]

		# collect props and values
		props = []
		query_vals = []
		for prop in values:
			props.append(prop + "=%s")
			query_vals.append(values[prop])
		query_vals.append(row_id)

		# create SQL UPDATE statement
		parts = ["UPDATE ", table, " SET "]
		parts.append(",".join(props))
		parts.append(" WHERE ")
		parts.append(id_col)
		parts.append("=%s")
		query = "".join(parts)

		# Recording all query objects
		where_clauses = [{id_col : row_id}]

		return_value = self.batch_execute(query, query_vals)
		self.record_sql_queries(table, values, SQLRecordType.UPDATE_ROW, False, 0, where_clauses)
		# execute statement
		return return_value

	# not in use currently in 1.8.0
	def update_record_where(self, table, where_values, values, replaceMap=None) -> bool:

		# exit if no work
		if values == None or len(values) == 0:
			return -1

		where_clauses = []
		where_value_list = []
		where_clause_string = ''

		# if find and replace needed
		if replaceMap is not None:
			# get final dict based on the replace map
			values = DictProcessor.replaceProps(values, replaceMap)

			# get final table name based on the replace map
			if table in replaceMap:
				table = replaceMap[table]

		# Preparing the where clauses
		for col_name, col_value in where_values.items():
			if replaceMap is not None:
				if col_name in replaceMap:
					col_name = replaceMap[col_name]

			where_clauses.append(f"{col_name}=%s")
			where_value_list.append(col_value)

		where_clause_string = " AND ".join(where_clauses)

		# collect props and values
		props = []
		query_vals = []
		for prop in values:
			props.append(prop + "=%s")
			query_vals.append(values[prop])

		# create SQL UPDATE statement
		parts = ["UPDATE ", table, " SET "]
		parts.append(",".join(props))
		parts.append(" WHERE ")
		parts.append(where_clause_string)
		query = "".join(parts)

		# Adding values of where clauses
		query_vals = query_vals + where_value_list

		# execute statement
		return self.batch_execute(query, query_vals)


	def delete_record(self, table, id_col, row_id, replaceMap=None) -> bool:

		# if replacement required
		if replaceMap is not None:

			# get final col name based on the replace map
			if id_col in replaceMap:
				id_col = replaceMap[id_col]

			# get final table name based on the replace map
			if table in replaceMap:
				table = replaceMap[table]

		# create SQL DELETE statement
		parts = ["DELETE FROM ", table, " WHERE ", id_col, "=%s"]
		query = "".join(parts)
		query_vals = [row_id]

		# Recording sql queries
		where_clauses = [{id_col : row_id}]

		return_value = self.batch_execute(query, query_vals)
		self.record_sql_queries(table, None, SQLRecordType.DELETE_ROW, False, 0, where_clauses)
		# execute statement
		return return_value



	def delete_records(self, table, id_col, row_ids, replaceMap=None) -> bool:

		# exit if no work
		if row_ids == None or len(row_ids) == 0:
			return False

		# if replacement required
		if replaceMap is not None:

			# get final col name based on the replace map
			if id_col in replaceMap:
				id_col = replaceMap[id_col]

			# get final table name based on the replace map
			if table in replaceMap:
				table = replaceMap[table]

		# collect values
		placeholders = []
		query_vals = []
		where_clauses = []
		for row_id in row_ids:
			placeholders.append("%s")
			query_vals.append(row_id)
			where_clauses.append({id_col : row_id})

		# create SQL DELETE statement
		parts = ["DELETE FROM ", table, " WHERE ", id_col, " IN ("]
		parts.append(",".join(placeholders))
		parts.append(")")
		query = "".join(parts)


		return_value = self.batch_execute(query, query_vals)
		# Recording sql queries
		self.record_sql_queries(table, None, SQLRecordType.DELETE_ROWS, False, 0, where_clauses)

		# execute statement
		return return_value


	def delete_all_records(self, table) -> bool:

		# create SQL DELETE statement
		query = "TRUNCATE TABLE " + table

		return_value = self.batch_execute(query, [])
		# Recording sql queries
		self.record_sql_queries(table, None, SQLRecordType.DELETE_ALL_ROWS, False, 0, [])

		# execute statement
		return return_value
