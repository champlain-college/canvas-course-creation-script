#! python3
import csv, requests, json, pprint, time, sys, datetime, re, configparser, os
from threading import Timer
#################################################
## CONFIG                                      #
#################################################
config = configparser.ConfigParser()
config.read('config/config.ini')
token = config.get('auth', 'token')
header = {'Authorization': 'Bearer {}'.format(token)}
# CSVs
csv_ccotrad_source = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/_CCOTRAD2023.csv'
csv_ccotrad_output = '/Users/dan-selicaro/Documents/canvas-shells/csv/output/output-2023-CCOTRAD.csv'
csv_trad_faculty = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/enroll-trad-faculty.csv'
csv_source = '/Users/dan-selicaro/Documents/canvas-shells/csv/source/_CCOTRAD_2023.csv'
# ETC
################################################################################################
# Globals
################################################################################################
# Updating this sheet:
# 1 - Enter new terms in Canvas, and then run find_termIds to get their IDs. Add to terms_ list.
# 2 - Check Sections on new sheet for any new sections.
# 3 - Change template id in import_template()
# 4 - Verify course_name var has updated term: Fall 2022 etc
log_time = str(time.asctime(time.localtime(time.time())))
subaccount_ids = [
    {'CPS': 1633},
    {'Professional Development': 1947},
    {'eLearning': 2059},
    {'GRAD': 2076},
    {'Manually-Created Courses': 2617},
    {'Traditional': 3171},
    {'Center for Learning & Teaching': 15360},
    {'Online Course Syllabi': 15904},
    {'Information Systems': 16383},
    {'Special Projects': 16550},
    {'ACI': 15378},
    {'ORI': 15378},

    # GRAD subaccount
    {'MIT': 2078},
    {'MED': 2080},
    {'EMM': 2081},
    {'GEE': 2083},
    {'Annex': 6491},
    {'90': 6494},
    {'Shanghai': 8953},
    {'POD-Grad': 13031},
    {'MSL': 13124},
    {'Cooperrider': 13650},
    {'MSL-MASTER': 13681},
    {'Orientation': 14916},
    {'GEE-MASTER': 15000},

    # CPS Subaccount - 1633
    {'Test-Out': 2075},
    {'CKET': 17234},
    {'CRIT': 19003},
    {'MBA': 2077},
    {'DIM': 2079},
    {'HCMT-Undergrad': 2082},
    {'DFS': 2085},
    {'CPSSandbox': 5769},
    {'HCMT-GRAD': 6308},
    {'TAP': 6610},
    {'ACCT': 8699},
    {'ARTS': 8700},
    {'BLAW': 8701},
    {'CFDI': 8702},
    {'CMIT': 8703},
    {'COMM': 8704},
    {'CRIM': 8705},
    {'CYBR': 8706},
    {'DGMD': 21113},
    {'EBUS': 8707},
    {'ECON': 8708},
    {'ENGL': 8709},
    {'ESPT': 21115},
    {'HIST': 8710},
    {'HITS': 8711},
    {'MATH': 8712},
    {'MCOM': 8713},
    {'MGMT': 8714},
    {'MKCM': 20591},
    {'MMKT': 21117},
    {'MKTG': 8715},
    {'NETW': 8716},
    {'PHIL': 8717},
    {'PSYC': 8718},
    {'SCIE': 8719},
    {'SDEV': 8720},
    {'WEBD': 8721},
    {'WRIT': 8722},
    {'CAPS': 8723},
    {'MSEL': 11598},
    {'CPS Master Courses': 14656},
    {'OPSC': 14961},
    {'SOCI': 14986},
    {'Professional Development - CPS': 15021},
    {'Orientation Courses': 15378},
    {'CPS Development': 15393},
    {'POD': 15421},
    {'CMGT': 16166},
    {'HCMT': 16192},
    {'ELAW': 16194},
    # COR subaccount - 3172
    {'COR': 6265},
    {'CCC': 6266},
    {'Global Studies': 9653},
    {'COR-MASTER': 14500},
    {'COR-COMMON': 16173},
    {'Global Connections': 16193},
    # ITS Subaccount - 3176
    {'CIT': 6267},
    {'CSI': 6268},
    {'FOR': 6271},
    {'GPR': 6269},
    {'MTH': 6272},
    {'NET': 6273},
    {'RAD': 6274},
    {'SCI': 6275},
    {'SEC': 6276},
    {'WEB': 6277},
    {'CAP': 8979},
    {'ITS': 9416},
    {'DAT': 16206},
    {'SYS': 16369},
    # EHS Subaccount - 6106
    {'ASU': 20845},
    {'ENG': 6270},
    {'CRJ': 6299},
    {'EDU': 6300},
    {'ENP': 6301},
    {'HIS': 6302},
    {'LEG': 6303},
    {'PSY': 6304},
    {'SOC': 6305},
    {'SWK': 6306},
    {'Projects': 9627},
    {'EHS': 13046},
    {'MED': 16400},
    # CCM subaccount - 6107
    {'CCM': 6107},
    {'DFM': 2084},
    {'EVT': 6281},
    {'LAN': 6289},
    {'WRT': 6290},
    {'THE': 6291},
    {'GDD': 6292},
    {'GMD': 17831},
    {'IXD': 6293},
    {'EGD': 6294},
    {'COM': 6295},
    {'CRE': 6296},
    {'ART': 6297},
    {'MCM': 6298},
    {'SON': 13845},
    {'FLM': 13846},
    {'BRD': 15038},
    {'GAA': 16197},
    {'VCD': 17230},
    # BUS Subaccount - 6108
    {'ACC': 6278},
    {'BLW': 6279},
    {'ECN': 6280},
    {'GBP': 19809},
    {'INT': 6283},
    {'MGT': 6284},
    {'MKT': 6285},
    {'SPT': 6286},
    {'BUS': 6287},
    {'EBC': 6288},
    {'INV': 10082},
    {'FIN': 13847},
    {'MONT': 6215},
    {'DUBL': 6216},
    {'InSight': 6390},
    {'Faculty-Advisors': 9474},
    {'Res Life': 12259},
    {'SGA': 13140},
    {'Special Projects': 14562},
    {'Student Academic Support': 15775},
    {'SAP': 16200},
    {'LDR': 16207},
    {'DSDEV': 16176},

    #Trad sub account
    {'DDL': 19001},
    {'CMP': 20729},
    {'CCX': 19005}
                  ]
terms = [
    {"2022FA": 6135},
    {"2022TAF": 6187},
    {"2022FCO": 6213},
    {"2022F7A":6209},
    {"2022F7B": 6211},
    {"2022PTF":6217},
    {"2022FM1":6215},
    {"2022FM2":6219},
    # 2023
    {"2023S7B": 6393},
    {"2023SM2": 6399},
    {"2023SP": 6389},
    {"2023SCO": 6395},
    {"2023SM1": 6397},
    {"2023S7A": 6391},
    {"2023PTS": 6453},
    {"2023U7B": 6475},
    {"2023UM2": 6479},
    {"2023SU": 6481},
    {"2023UM1": 6477},
    {"2023U7A": 6473},
    {"2023FA": 6521},
    {"2023FM2": 6607},
    {"2023F7B": 6603},
    {"2023FM1": 6605},
    {"2023F7A": 6601},
    #2024
    {"2024SP": 6761},
    {"2024S7A": 6753},
    {"2024S7B": 6755},
    {"2024SM1": 6757},
    {"2024SM2": 6759},
    {"2024PTS": 6919},

    {"2024UM2": 6965},
    {"2024U7B": 6961},
    {"2024SU": 6957},
    {"2024UM1": 6963},
    {"2024U7A": 6959}


]
subs = []
terms2 = []


'''
TODO: 
Get sub account iDs
Get term IDs





'''


#################################################
## RETRIEVE TERM IDS IN CANVAS
#################################################
def find_termIds():
    url = "https://champlain.instructure.com/api/v1/accounts/283/terms?per_page=100"
    r = requests.get(url,headers=header)
    response =r.json()
    for x in response["enrollment_terms"]:
        print(x)

def find_termIds2():
    url = "https://champlain.instructure.com/api/v1/accounts/283/terms?per_page=100"
    payload = {"recursive": True}
    r = requests.get(url,headers=header,params=payload)
    response = r.json()
    pprint.pprint(response)
    for x in response:
        for term in x:
            terms2.append({term["name"]: x["id"]})
    while "next" in r.links.keys():
        r = requests.get(r.links["next"]["url"], headers=header)
        response = r.json()
        for x in response:
            terms2.append({x["name"]: x["id"]})

    pprint.pprint(terms2)

#################################################
## GET SUBACCOUNTS IN CANVAS - NOT IN USE
#################################################
def get_subaccounts():
    url = "https://champlain.instructure.com/api/v1/accounts/283/sub_accounts?per_page=100"
    payload = {"recursive": True}
    r = requests.get(url,headers=header,params=payload)
    response = r.json()
    for x in response:
        subs.append({x["name"]: x["id"]})
    while "next" in r.links.keys():
        r = requests.get(r.links["next"]["url"], headers=header)
        response = r.json()
        for x in response:
            subs.append({x["name"]: x["id"]})

#################################################
## GET (LOCAL) SUBACCOUNT ID -- PRODUCTION
#################################################
def get_subaccount_id(account_id_str):
    account_id_output = ''
    # for obj in subaccount_ids:
    for obj in subaccount_ids:
        for k, v in obj.items():
            if account_id_str == k:
                account_id_output = v
    return account_id_output
################################################
# GET (LOCAL) TERM ID - PRODUCTION
################################################
def get_term_id(term_str):
    term_id_output = ''
    for obj in terms:
        for k, v in obj.items():
            if term_str == k:
                term_id_output = v
    return term_id_output
########################################
# IMPORT TRAD TEMPLATE - PRODUCTION
# #####################################
def import_template(course_id):
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(course_id) + '/content_migrations'
    payload = {
        'migration_type': 'course_copy_importer',
        'settings[source_course_id]': 2210396
        #https://champlain.instructure.com/courses/2210396 -- Spring 2024 Trad template
        #https://champlain.instructure.com/courses/2079606 --- FALL 2023 Template
    }
    try:
        r = requests.post(url, params=payload, headers=header)
        r.raise_for_status()
        print('Template imported for course ID ' + str(course_id))
    except requests.exceptions.RequestException as e:
        print("OH SHIT -- Template not imported....")
        print(e)
        sys.exit(1)
def import_montreal_template(course_id):
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(course_id) + '/content_migrations'
    payload = {
        'migration_type': 'course_copy_importer',
        'settings[source_course_id]': 2025986 #MONT template 2024SP
    }
    try:
        r = requests.post(url, params=payload, headers=header)
        r.raise_for_status()
        print('MONTREAL template imported for course ID ' + str(course_id))
    except requests.exceptions.RequestException as e:
        print("OH SHIT -- Template not imported....")
        print(e)
        sys.exit(1)
def import_dublin_template(course_id):
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(course_id) + '/content_migrations'
    payload = {
        'migration_type': 'course_copy_importer',
        'settings[source_course_id]': 2215358 #DUBL template 2024SP
    }
    try:
        r = requests.post(url, params=payload, headers=header)
        r.raise_for_status()
        print('DUBLIN template imported for course ID ' + str(course_id))
    except requests.exceptions.RequestException as e:
        print("OH SHIT -- Template not imported....")
        print(e)
        sys.exit(1)
################################################
# PUBLISH COURSES - PRODUCTION
################################################
def publish_course(course_id):
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(course_id)
    payload = {'offer': True}
    try:
        r = requests.put(url, headers=header, params=payload)
        r.raise_for_status()
        result = r.json()
        print("Course Published")
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
################################################
# UNPUBLISH COURSES - NOT IN USE
################################################
def unpublish_course(course_id):
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(course_id)
    payload = {'offer': False}
    try:
        r = requests.put(url, headers=header, params=payload)
        r.raise_for_status()
        result = r.json()
        print('Course unpublished.')
        print('https://champlain.instructure.com/courses/' + str(course_id))
        print()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
################################################
# ENROLL TRAD FACULTY - PRODUCTION
################################################
def enroll_faculty(course_sis,user_sis):
    csv_faculty = open(csv_trad_faculty, 'w', newline='')
    csv_faculty_writer = csv.writer(csv_faculty)
    csv_faculty_writer.writerow([
        "course_id","user_id","role","status"
    ])

    csv_faculty_writer.writerow([
        course_sis,user_sis,"teacher","active"
    ])
    csv_faculty.close()

    def sis_import():
        url = "https://champlain.instructure.com/api/v1/accounts/283/sis_imports"
        f = open(os.path.expanduser("~/Documents/canvas-shells/csv/source/enroll-trad-faculty.csv"))
        files = {"attachment": f}
        try:
            r = requests.post(url, headers=header, files=files)
            data = r.json()
            print('Teacher enrolled: ' + str(user_sis))
        except requests.exceptions.RequestException as e:
            print("ERROR - Teacher not enrolled...")
            print(e)
            sys.exit(1)

    sis_import()
def set_features(sis_course_id):
    # DS: This enables the New Analytics and new Quizzes in the course.
    url = "https://champlain.instructure.com/api/v1/courses/sis_course_id:" + str(sis_course_id) + "/features/flags/analytics_2"
    url2 = "https://champlain.instructure.com/api/v1/courses/sis_course_id:" + str(sis_course_id) + "/features/flags/quizzes_next"
    payload = {"state": "on"}
    try:
        print("Setting Features....")
        r = requests.put(url, headers=header, params=payload)
        result = r.json()
        print("New Analytics feature set.")

        r2 = requests.put(url2, headers=header, params=payload)
        result = r2.json()
        print("New Quizzes feature set.")

    except requests.exceptions.RequestException as e:
        print("ERROR -- Features NOT SET!")
        print(e)
        sys.exit(1)
def external_tools_lookup(courseID):
    data_set = [] #reset our array
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(courseID) + '/external_tools?per_page=100'
    response = requests.get(url,headers=header)
    external_tools_data = response.json()

    for external_tool in external_tools_data:
        data_set.append(external_tool)

    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'])
        external_tools_data = response.json()
        for external_tool in external_tools_data:
            data_set.append(external_tool)
    pprint.pprint(data_set)

def check_for_assignment_and_delete_if_so(courseID):
    data = []
    group_id = ""
    def delete_groups(courseID, group_id):
        url = 'https://champlain.instructure.com/api/v1/courses/' + str(courseID) + '/assignment_groups/' + str(
            group_id)
        response = requests.delete(url, headers=header)
        r = response.json()
        print(response.status_code)
        print("Freekin deleted.")
        print('https://champlain.instructure.com/api/v1/courses/' + str(courseID))
    url = 'https://champlain.instructure.com/api/v1/courses/' + str(courseID) + '/assignment_groups'
    response = requests.get(url,headers=header)
    r = response.json()
    print(response.status_code)
    if not r:
        print("nope.")
        pass
    if r:
        id = r[0]['id']
        print(r)
        print('yes')
        print(id)
        for x in r:
            data.append(x["id"])
        if data:
            print("theres groups")
            pprint.pprint(data)
            for y in data:
                delete_groups(courseID, y)



################################################
# CREATE 2022 CPS AND TRAD SHELLS
################################################
def create_CPS_Trad_Shells():
    with open(csv_source, newline='') as csv_file:
        ## Output file
        csvOutputFile = open(csv_ccotrad_output, 'a', newline='')
        csvWriter = csv.writer(csvOutputFile)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            sis_id = row[0]
            course_code = row[1]
            short_name = row[2]
            course_account = row[3]
            term = row[4]
            division = row[5]
            method = row[6]
            location = row[7]
            start_date = row[8]
            end_date = row[9]
            added_on = row[10]
            faculty_id = str(row[11]).zfill(7)
            fac_first = row[13]
            fac_last = row[12]
            # reporting_term = row[17]
            course_name = row[15]
            # course_name = course_code + ": " + short_name + " - " + reporting_term + " ("+term+")"
            ## CREATE CCO COURSE ##
            error_msg = ''
            if division == 'CE':
                print('...........')
                print('CCO COURSE')
                print(course_code)
                print('...........')
                print('SIS ID: ' + str(sis_id))

                # Step 1: Get the Account ID:
                account_id_int = get_subaccount_id(course_account)
                if account_id_int == '':
                    account_id_int = 1633  # If no account id found, default to CPS sub-account
                    error_msg += 'Account'
                print('Course Account: ' + course_account + " (" + str(account_id_int)+")")

                # Step 2: Get the Term ID:
                term_id_int = get_term_id(term)
                if term_id_int == '':
                    term_id_int = 130  # Default Term
                    if error_msg == '':
                        error_msg += ' Term'
                print('Course Term: ' + term + " (" + str(term_id_int) + ")")

                # Step 3: Send the Request:
                earl = 'https://champlain.instructure.com/api/v1/accounts/' + str(account_id_int) + '/courses'
                payload = {
                    'course[sis_course_id]': sis_id,
                    'course[course_code]': course_code,
                    'course[name]': course_name,
                    'account_id': account_id_int,
                    'course[term_id]': term_id_int,
                    'course[show_announcements_on_home_page]': True,
                    'course[allow_student_forum_attachments]': True,
                    'course[allow_student_discussion_topics]': False,
                    'course[hide_distribution_graphs]': True
                }

                try:

                    r = requests.post(earl, headers=header, params=payload)
                    response = r.json()

                    if r.status_code == 400:
                        error_sis_msg = response['errors']['sis_source_id'][0]['message']
                        if error_sis_msg:
                            print(error_sis_msg + ', skipping...')
                            print()
                        continue

                    canvas_id = response["id"]
                    course_URL = 'https://champlain.instructure.com/courses/' + str(canvas_id)

                    print('Publishing course...')
                    publish_course(canvas_id)

                    print("CCO Course Successful -- " + course_URL)
                    print('.............................')
                    print()

                except requests.exceptions.RequestException as e:
                    print(e)
                    sys.exit(1)
                csvWriter.writerow([log_time,course_name,sis_id,canvas_id,course_account,term,division,method,start_date,end_date,error_msg,course_URL])
            ## CREATE TRAD COURSE ##
            elif not division == 'CE':
                print('...........')
                print('TRAD COURSE')
                print(course_code)
                print('...........')
                print('SIS ID: ' + str(sis_id))


                #1: Get the Account ID:
                account_id_int = get_subaccount_id(course_account)
                if location == "MONT":
                    account_id_int = 6215
                    print("Course Account: This is a MONT course.")
                if location == "DUBL":
                    account_id_int = 6216
                    print("Course Account: This is a DUBL course.")

                if account_id_int == '':
                    account_id_int = 3171
                    if error_msg != '':
                        error_msg += ' Account'
                print('Course Account: ' + course_account + " (" + str(account_id_int) + ") ")

                # Step 2: Get the Term ID:
                term_id_int = get_term_id(term)
                if term_id_int == '':
                    term_id_int = 130  # Default Term
                    error_msg += 'Term'
                print('Course Term: ' + term + " (" + str(term_id_int) + ") ")


                # Step 3: Send the Request:
                payload = {
                    'course[sis_course_id]': sis_id,
                    'course[course_code]': course_code,
                    'course[name]': course_name,
                    'account_id': account_id_int,
                    'course[term_id]': term_id_int,
                    'course[allow_student_discussion_topics]': False
                }
                if location == "DUBL":
                    timezone = {"course[time_zone]": "Europe/Dublin"}
                    payload.update(timezone)

                earl = 'https://champlain.instructure.com/api/v1/accounts/' + str(account_id_int) + '/courses'

                try:
                    r = requests.post(earl, headers=header, params=payload)
                    response = r.json()

                    if r.status_code == 400:
                        error_sis_msg = response['errors']['sis_source_id'][0]['message']
                        if error_sis_msg:
                            print(error_sis_msg + ', skipping...')
                            print()
                        continue
                    r.raise_for_status()
                    canvas_id = response['id']
                    course_URL = 'https://champlain.instructure.com/courses/' + str(canvas_id)

                    #Step 4: Import Template -- make sure template ID is correct!
                    if location == 'MONT':
                        import_montreal_template(canvas_id)
                    elif location == 'DUBL':
                        import_dublin_template(canvas_id)
                    else:
                        import_template(canvas_id)

                    #Step 5: If there is a faculty ID listed, enroll them.
                    if faculty_id and not faculty_id == "0000000":
                        try:
                            enroll_faculty(sis_id, faculty_id)
                            # print("Teacher Enrolled: " + fac_first + " " + fac_last + " (" + faculty_id + ")")
                        except:
                            error_msg+="Teacher Enrollment Error"
                            sys.exit(1)
                    else:
                        print("No teacher listed.")

                    # Step 6: Enable Features -- New Quizzes and New Analytics.
                    set_features(sis_id)


                    print('Publishing course...')
                    publish_course(canvas_id)
                    print("TRAD Course Creation Successful -- " + course_URL)
                    print('.............................')

                except requests.exceptions.RequestException as e:
                    print(e)
                    sys.exit(1)





                csvWriter.writerow(
                    [
                        log_time, course_name, sis_id, canvas_id, course_account, term, division, method, start_date,
                     end_date, error_msg, course_URL, faculty_id, fac_first, fac_last
                    ])
    csvOutputFile.close()

