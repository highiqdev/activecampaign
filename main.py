from flask import Flask, request, render_template
import json
import clean_data as cld

app = Flask("app",
            template_folder="templates",  # name of folder containing html templates
            static_folder="static"  # name of folder for static files
            )


@app.route("/", methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':

        # get the json file from the form
        # need to make sure this comes in as the same format the test creation did
        data = request.json

        # select from the dict the data we want to use
        # this might still work for new typeform (it does?)
        transformed_data = id.typeform_response_dict(data)

        for k, v in transformed_data.items():
            print('transformed data: ', k, ' - ', v)

        # create a dict with the agent info from typeform
        this_agent_dict = cld.agent_info_dict(transformed_data)

        for k, v in this_agent_dict.items():
            print('agent dict: ', k, ' - ', v)

        # using these is going to require a different way of handling a typeform json file
        # returns basic contact of agent dict from AC
        fetched_agent_info = ace.get_agent_contact_info(
            this_agent_dict['Agent Email'])  # email extracted from typeform json
        fetched_agent_info['Lead Type'] = this_agent_dict['Lead Type']
        fetched_agent_info['List Path'] = this_agent_dict['List Path']

        for k, v in fetched_agent_info.items():
            print('fetched info dict: ', k, ' - ', v)

        # returns dict of agent fields from AC via agent_id
        final_agent_info = ace.get_agent_fields(
            fetched_agent_info['Agent Contact ID'], fetched_agent_info)

        for k, v in fetched_agent_info.items():
            print('final info dict: ', k, ' - ', v)

        # get the list of lists from the activecampaign api
        lists = ace.get_all_lists('all lists updated.json')

        # write the lists available on activecampaign to a json file
        with open('pulled list data.json', 'w', encoding='utf-8') as f:
            json.dump(lists, f, ensure_ascii=False, indent=4)
            print('creating lists json file')

        # get the list id for the agent by type of lead
        list_id_dict = fp.return_agent_list_id(
            final_agent_info['Agent First Name'], final_agent_info['Lead Type'], lists)
        for k, v in list_id_dict.items():
            print('found list ids', k, ': ', v)

        # check if the list id is found, if not create it, update listGroups, and return list id
        updated_list_ids = ace.agent_list_update(
            final_agent_info, list_id_dict)
        for k, v in updated_list_ids.items():
            print('updated list ids: ', k, ': ', v)

        # # transform dataframe and add agent info to entries
        # # calls intake data to get the dataframe from csv
        # # calls add_agent_info to add agent info to dataframe
        clean_df = cld.combined_clean(final_agent_info)
        # print(clean_df.head())

        # # convert the dataframe to a list of dicts with pandas 'records' format
        contact_list_from_df = clean_df.to_dict('records')

        # '''reformat the dicts to match the activecampaign api
        # this needs to get adjusted to that it only pulls the UPDATE_CHUNK_SIZE number of dicts at a time
        # then we can put the remaining dicts in the pending list and update the api
        # '''
        contact_list = ace.reformat_contact_dict(
            contact_list_from_df[:UPDATE_CHUNK_SIZE], updated_list_ids['target list id'])
        pending_contact_list = ace.reformat_contact_dict(
            contact_list_from_df[UPDATE_CHUNK_SIZE:UPDATE_CHUNK_SIZE + 5], updated_list_ids['pending list id'])
        # # print(contact_list[:1]) # test to see if the dict is formatted correctly

        # # upload the list of dicts to the activecampaign api

        ###### final calls to push contacts to lists. ###########
        ace.update_lists_ac_api(contact_list)
        ace.update_lists_ac_api(pending_contact_list)

        return "webhook received"

    else:
        return "nothing"


app.run(host="0.0.0.0", port=8080)  # run the application


# ################################################
# UPDATE_CHUNK_SIZE = 300

# app = Flask("app",
#   template_folder="templates", # name of folder containing html templates
#   static_folder="static" # name of folder for static files
# )

# @app.route("/", methods=['GET', 'POST'])
# def submit():
#   if request.method == 'POST':
#     # get the json file from the form
#     data = request.json
#     # transform the json file into a dict
#     transformed_data = id.typeform_response_dict(data)
#     # create a dict with the agent info from typeform
#     this_agent_dict = cld.agent_info_dict(transformed_data)
#     # get the list of lists from the activecampaign api
#     lists = ace.get_all_lists('all lists updated.json')
#     # get the list id for the agent by type of lead
#     list_id_dict = fp.return_agent_list_id(this_agent_dict['Agent First Name'], this_agent_dict['Lead Type'], lists)
#     # check if the list id is found, if not create it and return list id
#     updated_list_ids = agent_list_update(this_agent_dict, list_id_dict)


#     # transform dataframe and add agent info to entries
#     # calls intake data to get the dataframe from csv
#     # calls add_agent_info to add agent info to dataframe
#     clean_df = cld.combined_clean(this_agent_dict)
#     print(clean_df.head())

#     # convert the dataframe to a list of dicts
#     contact_list_from_df = clean_df.to_dict('records')

#     '''reformat the dicts to match the activecampaign api
#     this needs to get adjusted to that it only pulls the UPDATE_CHUNK_SIZE number of dicts at a time
#     then we can put the remaining dicts in the pending list and update the api
#     '''
#     contact_list = ace.reformat_contact_dict(contact_list_from_df[:UPDATE_CHUNK_SIZE], updated_list_ids['target_list_id'])
#     pending_contact_list = ace.reformat_contact_dict(contact_list_from_df[UPDATE_CHUNK_SIZE:], updated_list_ids['pending_list_id'])
#     # print(contact_list[:1]) # test to see if the dict is formatted correctly

#     # upload the list of dicts to the activecampaign api
#     ace.update_lists_ac_api(contact_list)
#     ace.update_lists_ac_api(pending_contact_list)


#     return "webhook received"


#   else:
#     return "nothing"

# app.run(host="0.0.0.0", port=8080) # run the application
# ##############################################
