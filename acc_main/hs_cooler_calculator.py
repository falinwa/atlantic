import pandas as pd
import re
import pytesseract


def calculator(name):
    df = pd.read_excel("src/user/acc_main/data/hs_prices.xlsx", index_col="Pattern")
    if name[0:2] == "KW":
        return kw_calculator(name, df)
    else:
        return ks_calculator(name, df)


def find_pattern(name, df):
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


def ks_calculator(name, df):
    pattern = find_pattern(name, df)
    length, turbulator = find_length_turbulator(name)
    baseprice = df.loc[pattern,"Baseprice"]
    lengthprice = df.loc[pattern,"Lengthprice"]
    if turbulator:
        tb_pattern = name[:4] + "T"
        tb_lengthprice = df.loc[tb_pattern, "Lengthprice"]
        tb_baseprice = df.loc[tb_pattern, "Baseprice"]
        return (baseprice + tb_baseprice) + (lengthprice + tb_lengthprice)*length/100
    else:
        return baseprice + lengthprice*length/100


def kw_calculator(name, df):
    ks_name = name.replace("KW", "KS")
    ks_price = calculator(ks_name)
    xray_price = xray_calculator(ks_name, df)
    surplus = df.loc[ks_name[0:4]+"P","Baseprice"]
    return ks_price + xray_price + surplus


def xray_calculator(name, df):
    row = name[0:4] + 'X'
    return df.loc[row,"Baseprice"]


def hs_ocr(img):
    # Select part of image with product code
    cropped_img = img.crop((370, 1000, 2700, 2000))

    # OCR
    text = str(pytesseract.image_to_string(cropped_img)).replace(" ", "")
    for line in text.split("\n"):
        if "Type" in line:
            return line[4:]


### Tests ###
assert calculator("KS12-FEL-823TL3000") == 2580.4