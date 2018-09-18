import datetime
import sys
from prettytable import PrettyTable

supportedTags = {"INDI": 0, "NAME": 1, "SEX": 1, "BIRT": 1, "DEAT": 1, "FAMC": 1, "FAMS": 1, "FAM": 0, "MARR": 1,
                 "HUSB": 1, "WIFE": 1, "CHIL": 1, "DIV": 1, "DATE": 2, "HEAD": 0, "TRLR": 0, "NOTE": 0}

treeList = {}
individualList = {}


def addtag(isIndi, id, tag, value):
    if value is not '':
        if isIndi:
            if tag not in individualList[id].keys() or individualList[id][tag] == '':
                individualList[id][tag] = value
            else:
                if isinstance(individualList[id][tag], list):
                    individualList[id][tag] += [value]
                else:
                    individualList[id][tag] = [individualList[id][tag]] + [value]
        else:
            if tag not in treeList[id].keys() or treeList[id][tag] == '':
                treeList[id][tag] = value
            else:
                if isinstance(treeList[id][tag], list):
                    treeList[id][tag] += [value]
                else:
                    treeList[id][tag] = [treeList[id][tag]] + [value]


def parse(gedcomFile):
    zeroLevelId = ""
    prevTag = ""
    for line in gedcomFile:
        fileLines = line.split()
        level = int(fileLines[0])
        tag = fileLines[1]
        valid = "N"

        arguments = " ".join(fileLines[2:])
        # print("--> " + line.strip())
        if fileLines[1] == "NOTE":
            continue
        if ("INDI" in fileLines) or ("FAM" in fileLines):
            if (level == 0) and ((fileLines[2] == "INDI") or (fileLines[2] == "FAM")):
                zeroLevelTag = tag
                zeroLevelId = fileLines[1]
                valid = "Y"
                tag = fileLines[2]
                arguments = fileLines[1]
                if fileLines[2] == "INDI":
                    individualList[arguments] = {}
                    isIndi = True
                else:
                    treeList[arguments] = {}
                    isIndi = False
        elif (fileLines[1] in supportedTags.keys()) and (level in supportedTags.values()):
            if fileLines[1] == "DATE":
                addtag(isIndi, zeroLevelId, prevTag, arguments)
                # if isIndi:
                #     individualList[zeroLevelId][prevTag] = arguments
                # else:
                #     treeList[zeroLevelId][prevTag] = arguments
            else:
                addtag(isIndi, zeroLevelId, fileLines[1], arguments)
                # if isIndi:
                #     individualList[zeroLevelId][fileLines[1]] = arguments
                # else:
                #     treeList[zeroLevelId][fileLines[1]] = arguments
            if supportedTags[fileLines[1]] == level:
                valid = "Y"
        prevTag = tag
        # print("<-- " + str(level) + "|" + tag + "|" + valid + "|" + arguments)


def printtree():
    indiTable = PrettyTable(["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
    for id, args in individualList.items():
        if "NAME" not in args.keys():
            args["NAME"] = "NA"
        if "SEX" not in args.keys():
            args["SEX"] = "NA"
        if "BIRT" not in args.keys():
            args["BIRT"] = "NA"
            birth = datetime.date(1, 1, 1)  # just to prevent errors
        else:
            birth = datetime.datetime.strptime(args["BIRT"], "%d %b %Y").date()
        if "DEAT" not in args.keys():
            args["DEAT"] = "NA"
            age = datetime.date.today() - birth
        else:
            death = datetime.datetime.strptime(args["DEAT"], "%d %b %Y").date()
            age = death - birth
        if "FAMC" not in args.keys():
            args["FAMC"] = "NA"
        if "FAMS" not in args.keys():
            args["FAMS"] = "NA"
        indiTable.add_row(
            [id, args["NAME"], args["SEX"], args["BIRT"], age.days // 365, args["DEAT"] == "NA", args["DEAT"],
             args["FAMC"], args["FAMS"]])
    famTable = PrettyTable(
        ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
    for id, args in treeList.items():
        if "MARR" not in args.keys():
            args["MARR"] = "NA"
        if "DIV" not in args.keys():
            args["DIV"] = "NA"
        if "HUSB" not in args.keys():
            args["HUSB"] = "NA"
            husbname = "NA"
        else:
            husbname = individualList[args["HUSB"]]["NAME"]
        if "WIFE" not in args.keys():
            args["WIFE"] = "NA"
            wifename = "NA"
        else:
            wifename = individualList[args["WIFE"]]["NAME"]
        if "CHIL" not in args.keys():
            args["CHIL"] = "NA"
        famTable.add_row([id, args["MARR"], args["DIV"], args["HUSB"], husbname, args["WIFE"], wifename, args["CHIL"]])
    print("Individuals")
    print(indiTable.get_string(sortby="ID"))
    print("Families")
    print(famTable.get_string(sortby="ID"))


if __name__ == "__main__":
    with open(sys.argv[1], "r") as file:
        gedcomFile = file.readlines()
    parse(gedcomFile)
    printtree()
