from pathlib import Path
import re
import os
import subprocess
import sys

BANNER = '\r\n ****     **                  *******   **                         \n/**/**   /**                 /**////** //   *****   *****   **   **\n/**//**  /**  *****   ****** /**    /** ** **///** **///** //** ** \n/** //** /** **///** **////**/**    /**/**/**  /**/**  /**  //***  \n/**  //**/**/*******/**   /**/**    /**/**//******//******   /**   \n/**   //****/**//// /**   /**/**    ** /** /////** /////**   **    \n/**    //***//******//****** /*******  /**  *****   *****   **     \n//      ///  //////  //////  ///////   //  /////   /////   //      \n'
EXCLUDE_EXTENSIONS = ['.png', '.gz', '.svg', '.kotlin_metadata', '.ttf', '.so']
EXCLUDE_HOSTS = ['schemas.android.com',
                'www.googleapis.com',
                'developer.mozilla.org']


class bcolors:
    GREEN = '\033[1;32m'
    END = '\033[1;m'
    INFO = '\033[1;33m[!]\033[1;m'
    QUE = '\033[1;34m[?]\033[1;m'
    BAD = '\033[1;31m[-]\033[1;m'
    GOOD = '\033[1;32m[+]\033[1;m'
    RUN = '\033[1;97m[~]\033[1;m'


def getFileInput():
    if len(sys.argv) > 1:
        apkFilePath = sys.argv[1]
        if os.path.exists(apkFilePath):
            return apkFilePath
        else:
            raise Exception(
                "The specified file is not valid or it doesn't exist")
    else:
        raise Exception("No file was provided")


def getFileBasename(file):
    filename, _ = os.path.splitext(file)
    basename = filename.split('/')[-1]
    return basename


def isItemInList(item, excludeItens):
    contains = [element for element in excludeItens if(element in item)]
    return contains


def listFiles(dir):
    fileList = []
    for root, __, files in os.walk(dir):
        for name in files:
            filepath = f"{root}{os.sep}{name}"
            _, file_extension = os.path.splitext(name)
            if not isItemInList(name, EXCLUDE_EXTENSIONS):
                fileList.append(filepath)
    return fileList


def extractUrlFromString(data):
    rgx = "[\"'\`](https?:\/\/|\/)[\w\.-\/]+[\"'\`]"
    match = re.finditer(rgx, data)
    matchList = [x.group() for x in match]
    return matchList


def unpackApk(apkFilePath, outPath):
    print(f"{bcolors.RUN}Unpacking files{bcolors.END}\n")
    command = f"apktool d {apkFilePath} -o {outPath} -fq"
    response = subprocess.run(
        command, shell=True, capture_output=True, stdin=subprocess.DEVNULL)
    return response


def analyzeFileList(filelist):
    matches = []
    for file in filelist:
        try:
            data = Path(file).read_text()
            match = extractUrlFromString(data)
            matches.extend(match)
        except:
            print(f"\n{bcolors.BAD}Unable to read - {file }, ignoring...\n")
            pass
    return matches


def extractUrls(apkUnpackedPath, apkFilePath):
    print(f"{bcolors.RUN}Extracting Urls{bcolors.END}")
    basename = getFileBasename(apkFilePath)
    outTxt = f"{basename}.txt"
    unpackedFileList = listFiles(apkUnpackedPath)
    matches = analyzeFileList(unpackedFileList)
    matchesFiltered = filter(
        lambda item: not isItemInList(item, EXCLUDE_HOSTS), matches)
    matchesFormmated = [s + '\n' for s in matchesFiltered]
    with open(outTxt, 'w') as fw:
        fw.writelines(matchesFormmated)
        print(
            f"{bcolors.GREEN}Created file '{outTxt}' containing the extracted urls.{bcolors.END}\n")
    print(f"{bcolors.END}Done!\n")
    return matches


def main():
    print(f"{bcolors.GREEN}{BANNER}{bcolors.END}")
    print(f"{bcolors.GREEN}by Whitehorse{bcolors.END}\n")
    apkFilePath = getFileInput()
    outPath = getFileBasename(apkFilePath)
    unpackProcecssResponse = unpackApk(apkFilePath, outPath)
    if(unpackProcecssResponse.returncode == 0):
        extractUrls(outPath, apkFilePath)
    else:
        print(f"{bcolors.BAD}Failed to unpack the target file. \nError:{unpackProcecssResponse.stderr} \r\nStdout:{unpackProcecssResponse.stdout}")


if __name__ == "__main__":
    main()
