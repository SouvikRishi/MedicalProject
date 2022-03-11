import boto3

text11 = """One.
Gomes date of birth in june 1st 1970 uh Hispanic gentleman who is here to stop his care, been having knee brace.
Also dizziness describes every has been a sensation with um in balance, has been in the emergency room several times for this problem.
He has been told that there's no significant abnormalities in the work up.
He denies a really noticed if he knows and no you're pains on the way lost on the rex year.
Past medical history significant for episodes with this in this medications hey takes meclizine 12 point 5 mg three times a day as needed for dizziness.
Allergies none.
Social history hip does not smoke cigarettes and alcohol, use of harmony.
History significant for uh they, with this.
Melena, this his mother, his father has had career two cc's and review of system is a junior in the fevers, no shows here as a child knee surgery, knee pain, celexa, the cough, This patient protection, assurance of breath.
G. I.
No National barbering, june or dysuria, hematuria, hematological, no no bleeding or bruising on the rle, surgical.
There is no headaches and no bomb, arms or legs weakness.
Objective hey is in no distress, temperature 97.80 pressure 1 32/80 pulse o about 72 respiratory rate of 18, oxygen saturation 92% on room air hit in a, a traumatic tumor, cephalic ear exam significant for normal tympanic membranes.
Next, no jugular distention and no carotid bruit.
Heart regular rate and rhythm.
Normal s one, s two.
No murmurs have been positive sounds, soft, nontender, nondistended.
No guarding, a ribbon next number 18 mile right exam, container strength 12 are intact.
Deep tendon reflexes are two plus at the knees and at the elbows.
Normal ambulation.
Assessment and plan um vertigo uh recommend to bomb get a CT Scan, low dye.
Brain, continue with meclizine, but in a cbc, cmp and follow up in one week.
"""
text12 = "Hello. How are you? Hi. Good. How are you? I understand that you have headaches. Yes, I think Any headaches that don't let me work. When do you get the headaches? The headaches? Come on. When I skip meals at times, I have to skip me. Also, that I couldn't go to meetings. And after a few hours, like headaches. How long does the headaches last? About 10 hours. And the patient changes. No changes. And this instituted to the light. Yeah. On with the orders to"
tx = "Good morning i have abdominal pain. Tell me more i got nausea and i have a burning sensation. Lewes ferry food and spicy foods. Do you hear that rehab no no diarrhea. Stop pretending you losing any weight. No weight loss now. Any loss of appetite. No you think it's cancer. I don't think it's cancer do i boil spicy foods greasy foods and coffee"

client = boto3.client(service_name='comprehendmedical', region_name='us-east-1')

result = client.detect_entities(Text= text11)
response = client.infer_icd10_cm(Text=text11)

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

icd10_info = dict()

icd10_entities = response['Entities']
for icd10_entity in icd10_entities:
    trait = ''
    trait_score = []
    for t in icd10_entity['Traits']:
        # print(t)
        trait = trait + t['Name'] + '_'
        # print(t['Score'])
        trait_score = trait_score+[float("{:.3f}".format(t['Score']))]
    trait = trait[:-1]
    if trait == "":
        continue
    key = trait
    icd10concept_list = []
    for concept in icd10_entity['ICD10CMConcepts']:
        icd10concept_list.append((concept['Description'],concept['Code'],concept['Score']))
    # print(icd10concept_list)

    if key in icd10_info.keys():
        icd10_info[key].append([icd10_entity['Text'],trait_score,icd10concept_list])
    else:
        icd10_info[key] = [[icd10_entity['Text'],trait_score,icd10concept_list]]

print(icd10_info)
# print(result)
# print(response)

