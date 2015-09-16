import os

from Deadline.Plugins import *
from Deadline.Scripting import *


def GetDeadlinePlugin():
    return PythonPlugin()


def CleanupDeadlinePlugin(deadlinePlugin):
    deadlinePlugin.Cleanup()


class PythonPlugin (DeadlinePlugin):

    def __init__(self):
        self.InitializeProcessCallback += self.InitializeProcess
        self.RenderExecutableCallback += self.RenderExecutable
        self.RenderArgumentCallback += self.RenderArgument
        self.StartupDirectoryCallback += self.StartupDirectory

    def Cleanup(self):
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback

        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback
        del self.StartupDirectoryCallback

    def HandleSampleProgress(self):
        start = self.GetRegexMatch(1)
        end = self.GetRegexMatch(2)
        self.SetProgress(int(start) * 100/int(end))

    def InitializeProcess(self):

        self.StdoutHandling = True
        self.PluginType = PluginType.Simple
        self.SingleFramesOnly = True
        self.AddStdoutHandlerCallback(".*Transfering: ([0-9]+)/([0-9]+).*").HandleCallback += self.HandleSampleProgress

        pythonPath = self.GetEnvironmentVariable("PYTHONPATH").strip()
        addingPaths = self.GetConfigEntryWithDefault("PythonSearchPaths", "").strip()

        if addingPaths != "":
            addingPaths.replace(';', os.pathsep)

            if pythonPath != "":
                pythonPath = pythonPath + os.pathsep + addingPaths
            else:
                pythonPath = addingPaths

            self.LogInfo("Setting PYTHONPATH to: " + pythonPath)
            self.SetEnvironmentVariable("PYTHONPATH", pythonPath)

    def RenderExecutable(self):
        version = self.GetPluginInfoEntry("Version")

        exeList = self.GetConfigEntry("Python_Executable_" + version.replace(".", "_" ))
        exe = FileUtils.SearchFileList(exeList)
        if exe == "":
            self.FailRender( "Python " + version + " executable was not found in the semicolon separated list \"" + exeList + "\". The path to the render executable can be configured from the Plugin Configuration in the Deadline Monitor." )
        return exe

    def RenderArgument( self ):
        # change dis
        scriptFile = os.path.join(self.GetPluginDirectory(), 'at_client.py')

        arguments = self.GetPluginInfoEntryWithDefault("Arguments", "")
        arguments = RepositoryUtils.CheckPathMapping(arguments)

        auxFiles = self.GetAuxiliaryFilenames()

        if len(auxFiles) < 2:
            self.FailRender('Please submit required files list and config file.')

        requirementsFile = auxFiles[0]
        configFile = auxFiles[1]

        if SystemUtils.IsRunningOnWindows():
            scriptFile = scriptFile.replace("/", "\\")
        else:
            scriptFile = scriptFile.replace("\\", "/")

        return "\"" + scriptFile + "\" " + "--file=\"" + requirementsFile + "\" " + "--config=\"" + configFile + "\" " + arguments

    def StartupDirectory(self):
        return self.GetPluginDirectory()
