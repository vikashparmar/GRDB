import re
from dicttoxml import dicttoxml # pip install dicttoxml
from lxml import etree #pip install lxml
from framework.system.LogService import LogService

class XMLCreator:
    @staticmethod
    def create(element, schema_type=None):

        """ use case of this function is to create xml format from dictonary and writes into xml file"""
        # for id,element in enumerate(data):
            # print(element)
        file_name = element['transfer']
        data = element['data']

        if schema_type == "TS":
            xml = dicttoxml(data,attr_type = False,custom_root='TransshipmentShipmentStatus xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.wwalliance.com/wiki/images/a/a7/WWA_Transshipment_Shipment_Status_version_1.0.0.xsd"')
        elif schema_type in ("sequence_schema", "link_delink"):
            xml = dicttoxml(data,attr_type = False,custom_root='ShipmentStatus xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNameSpaceSchemaLocation="http://www.wwalliance.com/wiki/images/d/d4/WWA_Shipment_Status_version_1.1.0.xsd"')
        elif schema_type == "send_same_status":
            xml = dicttoxml(data,attr_type = False,custom_root='CargoTracking xmlns="http://www.kuehne-nagel.com/lex/cargotracking/edi"')
        else:
            xml = dicttoxml(data,attr_type = False,custom_root='ShipmentStatus xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNameSpaceSchemaLocation="http://www.wwalliance.com/doc/wwa-ei/Shipment_Status/1.0.0/Schema/WWA_Shipment_Status_version_1.0.0.xsd"')
        
        xml_decode = xml.decode()

        parser = etree.XMLParser(recover=True,remove_blank_text=True,strip_cdata=False,resolve_entities=False)

        doc = etree.fromstring(xml,parser=parser)

        doc = etree.tostring(doc, encoding='UTF-8', method='xml',xml_declaration=True,pretty_print=True,inclusive_ns_prefixes=True)

        split_detail = (doc.decode()).split('\n')
        
        split_detail = [XMLCreator.data_manipulate(r) for r  in split_detail]
        
        split_join = '\n'.join(split_detail)
            
        message = element['message_log_detail']
        message['insert'] = False
        
        count_data = {
            "count" : 0
        }
        LogService.print(f"SSE: count {count_data}")
        if count_data['count'] != 0:
            LogService.print(f"SSE: file was already processed with Itemid {message['iItemID']} with status_code {message['cStatuscode']} for memberid {message['iMemberID']}")
        else:
            xmlfile = open('framework/SSE/files_generated/' + file_name, "w")
            xmlfile.write(split_join)
                
            xmlfile.close()
            message['insert'] = True

            # adding the attribute into the tags (send_same_status)
            if schema_type == "send_same_status":
                attributes = element.get('attributes')
                # read the file
                tree = etree.parse('framework/SSE/files_generated/' + file_name)
                tree_root = tree.getroot()
                tree_root[0].attrib["id"] = attributes.get('Id')
                for child in tree_root[1][0]:
                    if child.tag == "{http://www.kuehne-nagel.com/lex/cargotracking/edi}container":
                        child.attrib["number"] = attributes.get('ContainerNumber')
                    else:
                        child.attrib["code"] = attributes.get('StatusCode')
                tree.write('framework/SSE/files_generated/' + file_name, xml_declaration=True, encoding='UTF-8')
            
            LogService.print(f"SSE: file was processed with Itemid {message['iItemID']} with status_code {message['cStatuscode']} for memberid {message['iMemberID']} with filename {file_name}")
        
    def data_manipulate(tag_value):
        """
        finds the uncompleted tags of each line and insert the appropriate tag
        """
        try:
            search_tag = re.search('\s+\<\w+\/\>$',tag_value)
            if search_tag:
                tag_value = re.sub('\/','',search_tag.group(0))+'</'+re.findall('[a-zA-z]+',search_tag.group(0))[0]+'>'
            return tag_value
        except Exception as e:
            LogService.print(f"SSE: tag_value {str(e)}")