import xml.etree.ElementTree as ET
import pandas as pd

def createDataForDrug():
    tree = ET.parse('.\\XMLDATA\\icd10cm_drug_2022.xml')
    root = tree.getroot()

    headingDict = dict()
    for headings in root.iter('head'):
        headingDict[headings.attrib['col']] = headings.text

    df = pd.DataFrame(columns=headingDict.values())


    for mainterm in root.iter('mainTerm'):
        row = dict()
        title = mainterm.find('title').text
        row['Substance'] = title
        # print(title)
        for data in mainterm.iter('cell'):
            row[headingDict[data.attrib['col']]] = data.text
            # print(headingDict[data.attrib['col']], data.text)
        print(row)
        df = df.append(row,ignore_index=True)

    print(df.count())
    df.to_excel("icd10cm_drug.xlsx")

tree = ET.parse('.\\XMLDATA\\icd10cm_tabular_2022.xml')
root = tree.getroot()

df = pd.DataFrame(columns=["Title","Code"])
i = 0
for mainterm in root.iter('diag'):
    code = mainterm.find('name').text
    title = mainterm.find('desc').text
    row = {"Title":title, "Code":code}
    df = df.append(row, ignore_index=True)
    print("INFO: added new row", row)
    for each in mainterm.iter('inclusionTerm'):
        for i in each.iter('note'):
            row = {"Title": i.text, "Code": code}
            df = df.append(row, ignore_index=True)
            print("INFO: added new row", row)
df.to_excel("icd10cm_tabular.xlsx")

df_new = df[df.Code == "A05.1"]
print(df_new)
