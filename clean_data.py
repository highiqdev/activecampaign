import pandas as pd
import numpy as np


keep_col_list = ['FIRST', 'LAST', 'Prop_Address', 'Prop-City',
                 'Prop-State', 'Prop-Zip', 'PHONE1', 'PHONE2', 'EMAIL', ]

lead_types = ['Absentee-Owner', 'Downsize' 'Divorce', 'Likely-To-Sell',
              'Distressed', 'Motivated-Seller', 'Expired-Listing', 'Tax-Lein']

# AGENT_FIRST = "Harvey"
# AGENT_LAST = "Blankfeld"
# AGENT_PHONE = "702-581-4304"
# AGENT_EMAIL = "karlee@blankfeldgroup.com"
# AGENT_WEBSITE = "https://blankfeldgroup.com"
# AGENT_BROKERAGE = "The Blankfeld Group"
# BROKERAGE_ADDRESS = "7475 W. Sahara Ave #100"
# BROKERAGE_CITY = "Las Vegas, NV"
# AGENT_FULL_NAME = AGENT_FIRST + ' ' + AGENT_LAST

# agent_dict = {'Agent First Name': AGENT_FIRST,
#               'Agent Last Name': AGENT_LAST,
#               'Agent Phone': AGENT_PHONE,
#               'Agent Email': AGENT_EMAIL,
#               'Agent Website': AGENT_WEBSITE,
#               'Brokerage Name': AGENT_BROKERAGE,
#               'Brokerage Address': BROKERAGE_ADDRESS,
#               'Brokerage City': BROKERAGE_CITY,
#               'Lead Type': LEAD_TYPE
#               }


def agent_info_dict(incoming_dict):
    '''
    take typeform data dict and create agent info dict
    '''
    agent_dict = {}

    for key in incoming_dict.keys():

        if 'full name' in key:
            agent_dict['Agent First Name'] = incoming_dict[key].split()[0]
            agent_dict['Agent Last Name'] = incoming_dict[key].split()[1]
        elif 'website' in key:
            agent_dict['Agent Website'] = incoming_dict[key]
        elif 'email' in key:
            agent_dict['Agent Email'] = incoming_dict[key]
        elif 'phone' in key:
            agent_dict['Agent Phone'] = incoming_dict[key]
        elif 'name of their brokerage' in key:
            agent_dict['Brokerage Name'] = incoming_dict[key]
        elif 'brokerage street' in key:
            agent_dict['Brokerage Address'] = incoming_dict[key]
        elif 'city' in key:
            agent_dict['Brokerage City'] = incoming_dict[key]
        elif 'state' in key:
            agent_dict['Brokerage State'] = incoming_dict[key]
        elif 'zip' in key:
            agent_dict['Brokerage Zip'] = incoming_dict[key]
        elif 'csv' in key:
            agent_dict['List Path'] = incoming_dict[key]
        elif 'which kind' in key.lower():
            agent_dict['Lead Type'] = incoming_dict[key]

    return agent_dict


def intake_data(agent_dict):
    if agent_dict['List Path']:
        CSV_ADDRESS = agent_dict['List Path']
    # problem here is probaby parsing the path with an R string. check the colab verison functioning well.
    # csv_url = f'{CSV_ADDRESS}'
        df = pd.read_csv(CSV_ADDRESS)
        print('df loaded')
        return df
    # # else:
    #     df = pd.read_csv(RAW_DATA) #from direct colab upload
    return df


def camel_name(name):
    cased_name = name[:1] + name[1:].lower()
    return cased_name


def drop_cols(df, keep_list):
    drop_list = [col for col in list(df.columns) if col not in keep_list]
    df.drop(drop_list, axis=1, inplace=True)


def add_agent_info(df, agent_dict):
    agent_keys = agent_dict.keys()
    for key in agent_keys:
        if "List" not in key:
            df[key] = agent_dict[key]


def fill_blank_email(df):
    '''
    fills empty email with name
    '''

    df['EMAIL'] = df['EMAIL'].fillna(
        df['FIRST'] + '.' + df['LAST'] + '@no-email.com')
    df = df.fillna(value="")
    df = df.replace("nan", "")
    return df


def captialize_first_letter_of_each_word(string):
    '''
    capitalize the first letter of each word in a string
    '''
    return ' '.join(word.capitalize() for word in string.split())


def address_fix(df, col_list):
    for col in col_list:
        df[col] = df[col].apply(captialize_first_letter_of_each_word)


def two_phone_merge(df, priority_phone, secondary_phone):
    # this modifies the dataframe in place to merge the two phone columns with preference to phone 2 (mobile)
    df[f'{priority_phone}'].fillna(df[f'{secondary_phone}'], inplace=True)
    df.drop(f'{secondary_phone}', inplace=True, axis=1)
    df.rename(columns={f'{priority_phone}': 'PHONE'}, inplace=True)
    df['PHONE'] = df['PHONE'].astype(str).apply(lambda x: x.split('.')[0])


def name_cap_fix(df, col_names):
    for name in col_names:
        df[f'{name}'] = df[f'{name}'].apply(camel_name)


def remove_zip_last4(zipcode):
    if zipcode > 99999:
        return int(zipcode / 10000)
    else:
        return int(zipcode)


def split_by_zip(df):
    '''
    group the dataframe by zipcode
    '''
    zips = list(df['Prop-Zip'].unique())
    zip_df_dict = {}
    for zip in zips:
        zip_df_dict[zip] = (df[df['Prop-Zip'] == zip])
    return zip_df_dict


def split_df_to_multiple_csv(df, length, name, zip):
    """
    This function splits the dataframe into multiple csv files.
    :param df: dataframe
    :param length: int
    :return: None
    """
    count = 1
    for i in range(0, len(df), length):
        df[i:i+length].to_csv(f'{name} {zip} - ' +
                              str(count) + '.csv', index=False)
        count += 1


def combined_split(dict_of_zips, agent_name, split_length):
    for key, value in dict_of_zips.items():
        split_df_to_multiple_csv(value, split_length, f'{agent_name}', key)


def combined_clean(agent_dict, keep_cols=keep_col_list):
    work_df = intake_data(agent_dict)
    drop_cols(work_df, keep_cols)
    add_agent_info(work_df, agent_dict)
    two_phone_merge(work_df, 'PHONE2', 'PHONE1')
    name_cap_fix(work_df, ['FIRST', 'LAST'])
    work_df = fill_blank_email(work_df)
    work_df['EMAIL'] = work_df['EMAIL'].apply(str.lower)
    work_df['Prop_Address'] = work_df['Prop_Address'].apply(
        captialize_first_letter_of_each_word)
    work_df['Prop-City'] = work_df['Prop-City'].apply(
        captialize_first_letter_of_each_word)
    work_df['Prop-Zip'] = work_df['Prop-Zip'].apply(remove_zip_last4)
    return work_df


def output_csvs(df, agent_dict, split_length):
    zips_dict = split_by_zip(df)
    agent_name = f"{agent_dict['Agent First Name']} {agent_dict['Agent Last Name']}"
    combined_split(zips_dict, agent_name, 300)


def append_agent_info(df, agent_dict):
    for k, v in agent_dict.items():
        df[agent_dict[k]] = df[agent_dict[v]]
