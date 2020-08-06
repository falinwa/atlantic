import pandas as pd
import re
import pytesseract


def calculator(name):
    """
    Base function to calculate price, takes price data form hs_prices.xlsx
    Input: Product name
    """
    # df = pd.read_excel("src/user/acc_main/data/hs_prices.xlsx", index_col="Pattern")
    df = pd.read_excel("/Users/rubenhias/PycharmProjects/odoo/atlantic/acc_main/data/hs_prices.xlsx", index_col="Pattern")
    if name[0:2] == "KW":
        return kw_calculator(name, df)
    else:
        return ks_calculator(name, df)


def find_pattern(name, df):
    """
    Finding matching pattern of name with RE
    :param name: Product name you are searching the pattern of
    :param df: Pandas dataframe of prices
    :return: The matching pattern in the database of the price
    """
    for pattern in list(df.index):
        re_code = pattern.replace("#", "\S")
        re_pattern = re.compile(re_code)
        if re.match(re_pattern, name):
            return pattern


def find_length_turbulator(name):
    index = name.rfind("L")
    length = int(name[index+1:])
    turbulator = name[index-1] == "T"
    return length, turbulator


def len_weight_calculator(name, df, basename, lengthname):
    """
    Calculate result from basevalue and lengthvalue with data from dataframe
    :param name: Product name
    :param df: Pandas dataframe from prices and weight
    :param basename: Column name in dataframe of basevalues
    :param lengthname: Column name in dataframe of lengthvalues
    :return: calculated result based on length of product and turbulator option
    """
    pattern = find_pattern(name, df)
    length, turbulator = find_length_turbulator(name)
    basevalue = df.loc[pattern, basename]
    lengthvalue = df.loc[pattern, lengthname]
    if turbulator:
        tb_pattern = name[:4] + "T"
        tb_basevalue = df.loc[tb_pattern, basename]
        tb_lengthvalue = df.loc[tb_pattern, lengthname]
        return (basevalue + tb_basevalue) + (lengthvalue + tb_lengthvalue)*length/100
    else:
        return basevalue + lengthvalue*length/100


def ks_calculator(name, df):
    """
    Calculate prices for KS Heat exchangers
    :param name: Product name
    :param df: Pandas dataframe of prices
    :return: Price of product
    """
    price = len_weight_calculator(name, df, "Baseprice", "Lengthprice")
    weight = len_weight_calculator(name, df, "Baseweight", "Lengthweight")
    return price, weight



def kw_calculator(name, df):
    """
    Calculate price and weight for KW heat exchangers
    :param name: Product name
    :param df: Pandas dataframe of prices
    :return: Price of product
    """
    ks_name = name.replace("KW", "KS")
    ks_price, ks_weight = calculator(ks_name)
    xray_price = xray_calculator(ks_name, df)
    surplus_price = df.loc[ks_name[0:4]+"P","Baseprice"]
    surplus_weight = df.loc[ks_name[0:4]+"P","Baseweight"]
    return ks_price + xray_price + surplus_price, ks_weight + surplus_weight


def xray_calculator(name, df):
    """
    Calculate price of x-ray option for certain heat exchanger
    :param name: Product name
    :param df: Pandas dataframe of prices
    :return: Price of option
    """
    row = name[0:4] + 'X'
    return df.loc[row,"Baseprice"]


def hs_ocr(img):
    """
    Get product name from HS-Cooler datasheet
    :param img: Datasheet as PIL Image
    :return: Product name
    """
    # Select part of image with product code
    cropped_img = img.crop((370, 1000, 2700, 2000))

    # OCR
    text = str(pytesseract.image_to_string(cropped_img)).replace(" ", "")
    for line in text.split("\n"):
        if "Type" in line:
            return line[4:]


### Tests ###
assert calculator("KS12-FEL-823TL3000")[0] == 2580.4