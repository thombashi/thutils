'''
@author: Tsuyoshi Hombashi
'''


class EnvironmentInfo:
    EKN_PythonVersion = "Python Version"
    EKN_ProgramVersion = "Program Version"
    EKN_DateTime = "Date Time"
    EKN_PlatformSystem = "Platform System"
    EKN_PlatformNode = "Platform Node"
    EKN_PlatformRelease = "Platform Release"
    EKN_PlatformVersion = "Platform Version"
    EKN_PlatformMachine = "Platform Machine"
    EKN_PlatformProcessor = "Platform Processor"
    KN_DistributionName = "Distribution Name"
    KN_DistributionVersion = "Distribution Version"

    @classmethod
    def getGeneralInfoMatrix(cls):
        import platform

        system, node, release, version, machine, processor = platform.uname()

        value_listlist = [
            [cls.EKN_PythonVersion, platform.python_version()],
            [cls.EKN_PlatformSystem, system],
            [cls.EKN_PlatformNode, node],
            [cls.EKN_PlatformRelease, release],
            [cls.EKN_PlatformVersion, version],
            [cls.EKN_PlatformMachine, machine],
            [cls.EKN_PlatformProcessor, processor],
        ]

        if system == "Linux":
            distname, version, _supported_dists = platform.dist()
            value_listlist.append([cls.KN_DistributionName, distname])
            value_listlist.append([cls.KN_DistributionVersion, version])

        return value_listlist

    @classmethod
    def getGeneralInfoDict(cls):
        return dict(cls.getGeneralInfoMatrix())
