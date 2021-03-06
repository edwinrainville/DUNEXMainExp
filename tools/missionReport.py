# deploymentReport.py
'''
@edwinrainville

Description: This script goes through all data after it has been offloaded and makes a daily report of the data

The daily report will include:
1. List of microSWIFTs that were deployed that day
2. A map all drifter tracks - color coded by time 

'''

# Import Statements
import pylatex
import pandas as pd
import microSWIFTTools
import datetime

def make_report(doc, mission_num, mission_dir_path, metadata_path):
    '''
    @edwinrainville

    Builds mission report from data and the metaData spreadsheet.
    '''
    # Read in metadata from the excel sheet
    dunex_xlsx = pd.read_excel(metadata_path)
   
    # Add document header
    header = pylatex.PageStyle("header")
    # Create left header
    with header.create(pylatex.Head("L")):
        header.append("Date : {}".format(datetime.date.today()))
    # Create center header
    with header.create(pylatex.Head("C")):
        header.append('DUNEX Project - University of Washington Group')
    # Create right header
    with header.create(pylatex.Head("R")):
        header.append(pylatex.simple_page_number())
    # Add Document Preamble and formatting
    doc.preamble.append(header)
    doc.change_document_style("header")

    # Add Heading
    with doc.create(pylatex.MiniPage(align='c')):
        doc.append(pylatex.LargeText(pylatex.utils.bold('microSWIFT Mission Number {}'.format(mission_num))))

    # Add Overview to document
    with doc.create(pylatex.Section('Overview')):
        # Time info     
        start_time = dunex_xlsx['Start Time'].iloc[mission_num]
        end_time = dunex_xlsx['End Time'].iloc[mission_num]
        doc.append('Mission #{0} was from {1} to {2} in UTC time. '.format(mission_num, start_time, end_time))

        # Forecast info
        Hs_forecast = dunex_xlsx['Forecasted Significant Wave Height, Hs [m]'].iloc[mission_num]
        Tp_forecasted = dunex_xlsx['Forecasted Peak Period, Tp [s]'].iloc[mission_num]
        Dp_forecasted = dunex_xlsx['Forecasted  Peak Direction, Dp [degrees]'].iloc[mission_num]
        doc.append('The forecasted conditions for the day were a significant wave height of {0} meters, \
                    a peak period of {1} seconds and the waves were coming from {2}. \
                    '.format(Hs_forecast, Tp_forecasted, Dp_forecasted))

        # Array type and deployment
        deployment = dunex_xlsx['Deployment Method'].iloc[mission_num]
        array = dunex_xlsx['Array Type'].iloc[mission_num]
        doc.append('Due to these forecasted conditions, we deployed the microSWIFTs via {0} in \
                     {1}. '.format(deployment, array))

        # People and Positions
        deployer_1 = dunex_xlsx['Deployer 1'].iloc[mission_num]
        deployer_2 = dunex_xlsx['Deployer 2'].iloc[mission_num]
        retriever_1 = dunex_xlsx['Retriever 1'].iloc[mission_num]
        retriever_2 = dunex_xlsx['Retriever 2/ Notetaker'].iloc[mission_num]
        doc.append( 'The positions for this deployment were {} as deployer 1, {} as deployer 2, {} as \
                    retriever 1 and {} as retriever 2 and the notetaker, respectively. '.format(deployer_1, deployer_2, retriever_1, retriever_2))

        # microSWIFT final check
        microSWIFT_check = dunex_xlsx['microSWIFTs checked by'].iloc[mission_num]
        doc.append('The final microSWIFT check that all lights were on and lids were secured before deployment was done by {}. '.format(microSWIFT_check))

        # microSWIFTs deployed
        microSWIFTs_deployed = dunex_xlsx['microSWIFTs Deployed'].iloc[mission_num]
        total_num_microSWFITs = dunex_xlsx['Total Number of microSWIFTs'].iloc[mission_num]
        doc.append('The microSWIFTs deployed during this mission were {0} for a total of {1} microSWIFTs. '.format(microSWIFTs_deployed, total_num_microSWFITs))

        # microSWIFTs retrieved
        microSWIFTs_retrieved = dunex_xlsx['microSWIFTs Retrieved'].iloc[mission_num]
        doc.append('The microSWIFTs retrieved today were {0}. '.format(microSWIFTs_retrieved))


        # Additional Notes
        additional_notes = dunex_xlsx['Deployment Notes'].iloc[mission_num]
        doc.append('The additional notes during the deployment from {0} were the following: '.format(retriever_2))
        with doc.create(pylatex.Itemize()) as itemize:
            itemize.add_item(additional_notes)
     
        # Data offload Notes
        data_offload_check = dunex_xlsx['Data Offloaded and Archived by'].iloc[mission_num]
        data_offload_notes = dunex_xlsx['Data Offload Notes'].iloc[mission_num]
        doc.append('The data from this mission was offloaded by {0} and the additional data offload notes were: '.format(data_offload_check))
        with doc.create(pylatex.Itemize()) as itemize:
            itemize.add_item(data_offload_notes)

    # Add Mission Map to the document
    with doc.create(pylatex.Section('Drift Track Map')):
        mission_nc_path = mission_dir_path + 'mission_{}.nc'.format(mission_num)
        figure_path = microSWIFTTools.missionMap(mission_num, mission_dir_path, mission_nc_path)
        with doc.create(pylatex.Figure(position='htbp')) as plot:
            plot.add_image('../' + figure_path, width=pylatex.utils.NoEscape(r'0.8\textwidth'), placement=pylatex.utils.NoEscape(r'\centering'))
            plot.add_caption('Map of Mission {} Drifters and most currrent measured bathymetry at the FRF.'.format(mission_num))

    # # Add running histogram of significant wave heights sampled
    # with doc.create(pylatex.Section('Histogram of Significant Wave heights sampled')):
    #     doc.append('Histogram of wave heights')

if __name__ == '__main__':

    # Define project directory
    project_dir = '../'

    # Define data directory 
    data_dir = 'microSWIFT_data/'
    metadata_path = project_dir + 'DUNEXMainExp_notes.xlsx'

    # Define mission number 
    mission_num = int(input('Enter Mission Number: '))

    # Define mission directroy
    mission_dir = 'mission_{}/'.format(mission_num)
    mission_dir_path = project_dir + data_dir + mission_dir

    # Create report and fill it with analysis of todays data
    doc_name_str = 'mission_{}_report'.format(mission_num)
    doc_path_str = mission_dir_path + doc_name_str
    geometry_options = {"margin": "0.7in"}
    doc = pylatex.Document(doc_path_str, geometry_options=geometry_options)
    make_report(doc, mission_num, mission_dir_path, metadata_path)

    # Generate the report
    doc.generate_tex()
    doc.generate_pdf(clean_tex=False)
