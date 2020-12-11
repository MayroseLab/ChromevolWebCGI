#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use JSON;
use File::Slurp;
use List::Util qw(first);
use List::MoreUtils qw(any  first_index);

use lib "/bioseq/chromEvol";
#use lib "/bioseq/chromEvol/webServer_files";
#use lib "/bioseq/bioSequence_scripts_and_constants";
use lib "../";
use chromEvol_CONSTS_and_Functions;

my $query = new CGI;
my $jobId = $query->param('jobId');
my $CheckMe = " XXX -Y";

my %jsonData;
$jsonData{'errorOccured'} = 0;
$jsonData{'jobId'} = $jobId;

#my $curJobDir = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId";
my $curJobDir = chromEvol_CONSTS_and_Functions::RESULTS_DIR_ABSOLUTE_PATH."/$jobId";
my $log 	  = "$curJobDir/".chromEvol_CONSTS_and_Functions::LOG_FILE;

# checking if jobId is valid
if (!($jobId =~ /^[0-9]+\z/))
{
	$jsonData{'errorOccured'} = 1;
	$jsonData{'error'} = "Job $jobId contains invalid characters";
}
else
{
	#my $curJobDir = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId";

	
	# checking if job directory exists
	if (-d $curJobDir)
	{
		my $dataResultsRef = &GetResultsData($jobId, $curJobDir);
		my %dataResults = %$dataResultsRef;
		
		%jsonData = (%jsonData, %dataResults);
	}
	else
	{
		$jsonData{'errorOccured'} = 1;
	    $jsonData{'error'} = "Job $jobId does not exists.";
	}
}


# parsing return data to json and returnig it to client
my $json = encode_json(\%jsonData);
print $query->header();
print "$json\n";


sub GetResultsData
{
	my ($jobId, $curJobDir) = @_;
	my %jsonData;
	
	$jsonData{'jobId'}		= $jobId;
	$jsonData{'ModelsNamesArr'}	= &ReadToArrayParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_SELECTED_MODELS,"");  
	$jsonData{'LinuxJobNumber'}	= &ReadFromFile("$curJobDir/qsub_job_num.dat"); 
	$jsonData{'jobStatus'}	= &GetJobStatus($jobId, $curJobDir);
	$jsonData{'pip_control'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PIP, "");
	
	$jsonData{'TreesDirArr'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"TreesDirArr"); 

	#my @ArrTreesPaths = split(',', $query->param('TreesDirArr'));
	#$jsonData{'TreesDirArr'} = $query->param('TreesDirArr');
	
	#$jsonData{'runningOptions'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"runningOptions");#$jsonData{'TreeType'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"Tree_Type");
	#$jsonData{'LocusTreeNumber'}	= &ReadToArrayParam("$curJobDir/SummaryDir/LocusTrees/".chromEvol_CONSTS_and_Functions::FILENAME_LOCUS_TREENUM_TXT,"");  
	#$jsonData{'TreeUserRemark'}	= &ReadFromFile("$curJobDir/TreeStatusRemark.txt","");  
	#Check for final files in Summary dir - enables to present partial results as well:
	#$jsonData{'species_final_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/FinalSpeciesList.txt"); 
	#$jsonData{'web_partition_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/web_partition.txt"); 
	#$jsonData{'msa_concat_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/".$jobId."-concat-aligned.fasta"); 
	#$jsonData{'locusTrees_zip_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/LocusTrees_".$jobId.".zip"); 
	#$jsonData{'AccessionsMatrix_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/AccessionsMatrix.csv"); 
	#$jsonData{'all_clusters_data_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/All_Clusters_data.csv"); 
	#$jsonData{'all_data_zip_ready'}	= &CheckIfFileExists("$curJobDir/chromEvol_Output_".$jobId.".zip"); 
	#$jsonData{'TreeFile_ready'}	= &CheckIfFileExists("$curJobDir/SummaryDir/Result_Tree_".$jobId.".tre"); 
	#$jsonData{'ParamsForWeb_ready'}	= &CheckIfFileExists("$curJobDir/params_for_web.txt"); 
	#$jsonData{'ParamsForWeb_ready'}	= &CheckIfFileExists("$curJobDir/chromevol_out/infer/infer_tree_100/BASE_NUM/chromEvol.res"); 
	
	#ChromEvol
	#$jsonData{'chromevol_mlAnc_base'}	= &ReadFromFile("$curJobDir/BASE_NUM/mlAncestors.tree",""); 
	#$jsonData{'chromevol_mlAnc_cnst_rate'}	= &ReadFromFile("$curJobDir/CONST_RATE_DEMI/mlAncestors.tree",""); 
	
	

	#$jsonData{'TreeMethod'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"Tree_Method");
	#$jsonData{'jobTimeEstimation'}	= &GetTimeEstimation($jobId, $curJobDir);
	#$jsonData{'files'}		= &GetOutputFiles($jobId);
	#$jsonData{'images'} 	= &GetOutputImages($curJobDir);
	
	#my $logText = &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::LOG_FILE, "");
	#my $logText = &ReadFromFile("$curJobDir/".$jobId.".log", "");
	#my $logText = &ReadFromFile("$curJobDir/msgs.txt", "");
	#$jsonData{'logText'} 	= $logText;

	#$jsonData{'summary'} 	= &ReadFromFile("$curJobDir/SummaryDir/summary_file.txt", "");
	#$jsonData{'summary'} =~ s/\n/<br>\n/g; # replace new line chars with html's <br>
	
	my $json_data_file = "${curJobDir}/JSON_data.txt";  
	open (JSON_F,">$json_data_file") or die ("COULD not open JSON data file");
	print JSON_F "jobId - ", $jsonData{'jobId'},"\n"; 
	print JSON_F "ModelsNamesArr - ",$jsonData{'ModelsNamesArr'},"\n";    
	print JSON_F "LinuxJobNumber - ",$jsonData{'LinuxJobNumber'},"\n";         
	print JSON_F "jobStatus - ",$jsonData{'jobStatus'},"\n";    
	print JSON_F "pip_control - ",$jsonData{'pip_control'},"\n";    
	print JSON_F "TreesDirArr - ",$jsonData{'TreesDirArr'},"\n";    
	print JSON_F "vTreesDirArr - ",$jsonData{'vTreesDirArr'},"\n";    
	close (JSON_F);
	
	
	return \%jsonData;
}

=pod
sub GetOutputFiles
{
	my $pathMB			= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/MB_LOG.txt";
	my $pathTree		= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/Result_Tree.tre";
	my $pathClusters	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/All_Clusters_data.txt";
	my $pathAlignment	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/$jobId-concat-aligned.fasta";

	my ($jobId) = @_;
	my @filesDict;
		
	my %curFile1;
	$curFile1{'name'} = "Tree";
	$curFile1{'path'} = $pathTree;
  	push (@filesDict, \%curFile1);
	 
	my %curFile2;
	$curFile2{'name'} = "MB_LOG.txt";
	$curFile2{'path'} = $pathMB;
  	push (@filesDict, \%curFile2);
	 
	my %curFile3;
	$curFile3{'name'} = "Clusters";
	$curFile3{'path'} = $pathClusters;
  	push (@filesDict, \%curFile3);
	 
	my %curFile4;
	$curFile4{'name'} = "Alignment";
	$curFile4{'path'} = $pathAlignment;
  	push (@filesDict, \%curFile4);
	 
    return \@filesDict;
}
=cut
	
sub GetJobStatus
{
	my ($jobId, $curJobDir) = @_;
	
	# error exist?
	if (&ReadErrorLogFileStatus($curJobDir))
	{
		#sendFailedEmail();
		return 'Error';
	}

	# is job id in queue?
	#my $qstatCmd = 'ssh bioseq@powerlogin qstat -r ';
	my $qstatCmd = 'ssh bioseq@powerlogin qstat -w -r -u bioseq';
	#my $qstat_qw_Cmd = 'ssh bioseq@powerlogin qstat -s p';
	my $qstat_qw_Cmd = 'ssh bioseq@powerlogin qstat -s'; #removed p since not working on power -> Check how to replace!!
	#my $qstatCmd = 'ssh bioseq@lecs2 qstat -r';
	
	my $qstatCmdResponse = `$qstatCmd`;	
	my $qstat_qw_CmdResponse = `$qstat_qw_Cmd`;	
	
	my @responseLines = split("\n", $qstatCmdResponse);
	my @response_qw_Lines = split("\n", $qstat_qw_CmdResponse);
	
	my $EndFile = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/countsFile";
	#$query->param('jobId');
	if (! -e $EndFile) {
		return 'Running';
	} else {
		
		return 'PASS';
	}
	
 	# is any output file missing?
	#my $pathMB		= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/MB_LOG.txt";
	#my $pathTree	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/Result_Tree.tre";
	#my $pathFasta	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/$jobId-concat-aligned.fasta";

	#if (! -f $pathMB)		{ return 'Failed'; }
	
	
		
	#if (! -f $pathFasta)	
	{ 
		my $StatusText = &ReadFromFile("$curJobDir/SummaryDir/FinalStatus.txt", ""); 	
		return $StatusText;  
	}
	
	return 'Finished'; # last email is sent from OTT...sh , not from here
}

sub GetTimeEstimation
{
	my ($jobId, $curJobDir) = @_;
	
	# error exist?
	#if (-e "$curJobDir/SummaryDir/FinalStatus.txt")
	#{ 
	#	return '';
	#}else {
	if (-e "$curJobDir/calc_time_vars.txt")
	{
		#Read from file and send back
		my $TimeEstimate = &ReadFromFile("$curJobDir/calc_time_vars.txt", "");
		return $TimeEstimate;
	} else {
		return '...Calculating estimated running time';
	}
	#}
}

sub ReadErrorLogFileStatus
{
	my ($curJobDir) = @_;
	
	my $errLog = "$curJobDir/".chromEvol_CONSTS_and_Functions::ERROR_STATUS_LOG_FILE;

	my $errStatus = ReadFromFile($errLog, 0);
	
	return $errStatus;
}



sub sendFailedEmail
{
	# exit if emailWasSent file exists (don't send again)
	my $filename = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/failedEmailWasSent";
	if (-e $filename) {
		return;
	}
	
	# email was not sent yet, create emailWasSent file
	unless(open FILE, '>'.$filename) {
		print "\nUnable to create $filename\n";
	}
	
	# send the email
	my $fnameEmail = "$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_EMAIL;
	my $email = ReadFromFile($fnameEmail, 0);
    chomp $email; # remove new line
	`perl /bioseq/chromEvol/sendLastEmail.pl --jobTitle "" --toEmail $email --id $jobId`;
	
}


# last email is sent from OTT...sh , not from here
=pod
#sub sendLastEmail
#{
#
#	my ($curJobDir) = @_;
#	
#	my $fnameEmail = "$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_EMAIL;
#	my $email = ReadFromFile($fnameEmail, 0);
#    chomp $email; # remove new line
#
#	#my $cmd = "perl /bioseq/chromEvol/sendLastEmail.pl --toEmail $email --id $jobId";
#	my $cmd = "perl /bioseq/chromEvol/sendLastEmail.pl --toEmail $email --id $jobId";
#	WriteToFile( $log, $cmd);
#	`$cmd`;
#	my $return_code = $? >> 8;
#	WriteToFile( $log, "cmd return code:" .$return_code);
#
#
#	my $cmd = "perl /data/www/cgi-bin/chromEvol/sendLastEmail.pl --toEmail $email --id $jobId";
#	WriteToFile( $log, $cmd);
#	`$cmd`;
#	$return_code = $? >> 8;
#	WriteToFile( $log, "cmd return code:" .$return_code);
#
#	use Sys::Hostname;
#    my $host = hostname;
#	WriteToFile( $log, $host);
#
#	return 0;
#}
=cut


