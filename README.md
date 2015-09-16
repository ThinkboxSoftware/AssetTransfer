Asset Transfer Script Library - Copright (c) Thinkbox Software Inc.

This library supports FTP, Filecatalyst, Robocopy, rsync, and SFTP file transfers.


COMMAND-LINE USAGE
------------------

Usage:
  python at_client.py --file=[path] --config=[path] <optional parameters> <flags>

Required Parameters:
  --file=[path]   	-> path to the file which contains the list of files to either download, or to upload
  --config=[path] 	-> path to the configuration file to use for this transfer
  
Optional Parameters:
  Note: These should be specified in the INI config file but can instead be specified via command line.
  --ip=[ip or hostname] -> server to connect to
  --port=[port number]  -> port to connect via
  --service=[service]   -> desired transfer protocol - available protocols are: ftp, filecatalyst, robocopy, rsync, sftp

Flags:
  Note: These should be specified in the INI config file but can instead be specified via command line
  --upload    		-> upload files - service by default will download files
  --overwrite 		-> force download of files even if local files exist and are identical


CONFIGURATION
-------------

The transfer client requires a configuration file with the following fields:
[Server]
  ip         		-> IP address of the server to connect to.
  port       		-> Port to connect via (Usually 21 for FTP/Filecatalyst/rsync, 22 for SFTP, not needed for robocopy)
  server_dir 	      	-> Server directory to work with.
			With all transfer mechanisms other than Robocopy, this is a subdirectory of the transfer protocol's user folder.
			For Robocopy, this must be a full path in Windows-style formatting. Example: C$\Data\robodata\new

[User]
  name 			-> Transfer protocol username
  pass 			-> Transfer protocol password

[Client]
  log			-> Desired log file location/name
  service		-> Transfer protocol to use. Options are: ftp, filecatalyst, robocopy, rsync, sftp
  target_dir		-> If doing a download, this defines where files will be downloaded to (as a full path)
  source_dir		-> If doing an upload, this defines where files will be uploaded from (as a full path)
  flags			-> Space separated flags to run. See command line flags.


FILECATALYST NOTE:
  If you are using File Catalyst, you must provide your licensed File Catalyst command line jar file. Place it in the following location:
    [asset transfer library directory]/api_objects/fc_cli

RSYNC NOTE:
  If you are using rsync, you must provide a private key in the api_objects/rsync directory.