

def format_st_button():
    script =  """ <style>div.stButton > button:first-child {
        box-shadow: 3px 4px 0px 0px #95aaf0;
        background-color:#446cf2;
        border-radius:18px;
        border:1px solid #ffffff;
        display:inline-block;
        cursor:pointer;
        color:#ffffff;
        font-family:Arial;
        font-size:15px;
        padding:2px 2px;
        text-decoration:none;
        text-shadow:0px 1px 0px #810e05;
        }
        div.stButton > button:hover {background-color:#0c0091; box-shadow: 3px 4px 0px 0px #0c0091; border:1px solid #0c0091}
        </style>
        """
    return script
 
def hover_size():
    hover_size = '''
        <style type="text/css">
        .hovertext text {
            font-size: 20px !important;
        }
        .legendtext {
            font-size: 10px !important;
        }
        </style>
        '''
    return hover_size

def tabs_font_size():
    font_size = '''
    <style>
    button[data-baseweb="tab"] {
    font-size: 20px;
    }
    </style>
    '''
    return font_size

