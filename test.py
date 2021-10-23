import boto3

text11 = "Good morning. Good morning Ryan. how old are you? 34 years old. Tell me more. I got nausea and I have a burning sensation to be Freddy Food and spicy foods. Yeah, The pain gets worse with spicy food and coffee. Do you hear? They're really no, no diarrhea. It's separate in the Are you losing any weight? No weight loss? No. In the loss of appetite. Know? Do you think it is cancer? No, I do not think it is cancer.  Do our boy the space of foods, greasy foods and coffee, Okay."
text12 = "Hello. How are you? Hi. Good. How are you? I understand that you have headaches. Yes, I think Any headaches that don't let me work. When do you get the headaches? The headaches? Come on. When I skip meals at times, I have to skip me. Also, that I couldn't go to meetings. And after a few hours, like headaches. How long does the headaches last? About 10 hours. And the patient changes. No changes. And this instituted to the light. Yeah. On with the orders to"
tx = "Good morning i have abdominal pain. Tell me more i got nausea and i have a burning sensation. Lewes ferry food and spicy foods. Do you hear that rehab no no diarrhea. Stop pretending you losing any weight. No weight loss now. Any loss of appetite. No you think it's cancer. I don't think it's cancer do i boil spicy foods greasy foods and coffee"
client = boto3.client(service_name='comprehendmedical', region_name='us-east-1')
result = client.detect_entities(Text= text11)


# print(result)

# # print(result.keys())
#
health_info = dict()
# treatment = dict()
medical_condition = dict()
medication = dict()


entities = result['Entities'];
for entity in entities:
    # print('Entity', entity)
    # print('Text: ', entity['Text'])
    # print('Category: ', entity['Category'])
    # print('Type: ', entity['Type'])
    trait = ''
    for t in entity['Traits']:
        trait = trait + t['Name'] + '_'
    trait = trait[:-1]
    # print('Trait: ', trait)
    # print()

    if entity['Category'] == 'PROTECTED_HEALTH_INFORMATION':
        key = entity['Type']
        if key in health_info.keys():
            health_info[key].append(entity['Text'])
        else:
            health_info[key] = [entity['Text']]

    if entity['Category'] == 'MEDICAL_CONDITION':
        key = trait
        if key in medical_condition.keys():
            medical_condition[key].append(entity['Text'])
        else:
            medical_condition[key] = [entity['Text']]

    if entity['Category'] == 'MEDICATION':
        key = entity['Type']
        if key in medication.keys():
            medication[key].append(entity['Text'])
        else:
            medication[key] = [entity['Text']]


print('PROTECTED_HEALTH_INFORMATION')
print(health_info)
print('MEDICAL_CONDITION')
print(medical_condition)
print('MEDICATION')
print(medication)
