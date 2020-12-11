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


my %jsonData;
$jsonData{'errorOccured'} = 0;
$jsonData{'jobId'} = $jobId;

$jsonData{'TREE_models'} = [];


#my $curJobDir = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId";
my $curJobDir = chromEvol_CONSTS_and_Functions::RESULTS_DIR_ABSOLUTE_PATH."/$jobId";
my $log 	  = "$curJobDir/".chromEvol_CONSTS_and_Functions::LOG_FILE;

for (my $indx = 1; $indx < 11; $indx++){
	my $model_file = "$curJobDir/ChromEvol_Tree_$indx/ChosenModel_LowAIC.txt";
	if (-e $model_file)
	{
		my $line = read_file($model_file);
		#$jsonData->{'TREE_models'}->[0] = $line;
		#push @{$jsonData->{'TREE_models'}}, $line;
		$jsonData{"Tree$indx\_Model"} = $line;
	} else {
		$jsonData{"Tree$indx\_Model"} = "NONE";
		#push @{$jsonData->{'TREE_models'}}, "NONE";
		#$jsonData{"CCDDFF_$indx"} = 'NONE';
	}
}

#my $model_file = "$curJobDir/ChromEvol_Tree_1/ChosenModel_LowAIC.txt";
#if (-e $model_file)
#{
#	my $line = read_file($model_file);
#	$jsonData{'CCDDFF'} = $line;
#}

#my $CCDDFF = &ReadFromFile("$curJobDir/ChromEvol_Tree_1/ChosenModel_LowAIC.txt", ""); 
#my @models_arr;
#for (my $indx = 1; $indx < 11; $indx++){
#	my $model_x = &ReadFromFile("$curJobDir/ChromEvol_Tree_1/ChosenModel_LowAIC.txt", ""); 
#	if ($model_x eq 'abc975'){
#		push(@models_arr,'None');
#	} else {
#		push(@models_arr,$model_x);
#	}
#}
#$jsonData{'CCDDFF'} = @models_arr;


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
	$jsonData{'StatusFlags_Arr'}	= &ReadToArrayParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_STATUS_FLAGS,"");  
	$jsonData{'BestModelsPerTreeArr'}	= &ReadToArrayParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_BEST_MODELS,"");  
	$jsonData{'MA_Ploidy_Flags_Arr'}	= &ReadToArrayParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_MA_PLOIDY_FLAGS,"");  
	$jsonData{'LinuxJobNumber'}	= &ReadFromFile("$curJobDir/qsub_job_num.dat"); 
	#$jsonData{'ModelAdequacy'}	= &ReadFromFile("$curJobDir/qsub_job_num.dat"); 
	$jsonData{'jobStatus'}	= &GetJobStatus($jobId, $curJobDir);
	$jsonData{'input_files_report'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_INPUT_REPORT, "");
	$jsonData{'chrom_counts_data'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_CHROM_COUNTS, "");
	$jsonData{'adequacy_data'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_ADEQUACY, "");
	$jsonData{'done_file'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_DONE_FILE, "");
	$jsonData{'pip_control'} 	= &ReadFromFile("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PIP, "");
	
	$jsonData{'TreesDirArr'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"TreesDirArr"); 
	$jsonData{'ploidy_ON'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"ploidy_ON"); 
	$jsonData{'radio-one'}	= &ReadParam("$curJobDir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT,"radio-one"); 

	#my @ArrTreesPaths = split(',', $query->param('TreesDirArr'));

		
	my $json_data_file = "${curJobDir}/JSON_data.txt";  
	open (JSON_F,">$json_data_file") or die ("COULD not open JSON data file");
	print JSON_F "jobId - ", $jsonData{'jobId'},"\n"; 
	print JSON_F "CCDDFF - ", $jsonData{'CCDDFF'},"\n"; 
	print JSON_F "ModelsNamesArr - ",$jsonData{'ModelsNamesArr'},"\n";    
	print JSON_F "BestModelsPerTreeArr - ",$jsonData{'BestModelsPerTreeArr'},"\n";    
	print JSON_F "LinuxJobNumber - ",$jsonData{'LinuxJobNumber'},"\n";         
	print JSON_F "jobStatus - ",$jsonData{'jobStatus'},"\n";    
	print JSON_F "pip_control - ",$jsonData{'pip_control'},"\n";    
	print JSON_F "input_files_report - ",$jsonData{'input_files_report'},"\n";    
	print JSON_F "chrom_counts_data - ",$jsonData{'chrom_counts_data'},"\n";    
	print JSON_F "adequacy_data - ",$jsonData{'adequacy_data'},"\n";    
	print JSON_F "done_file - ",$jsonData{'done_file'},"\n";    
	print JSON_F "TreesDirArr - ",$jsonData{'TreesDirArr'},"\n";    
	print JSON_F "vTreesDirArr - ",$jsonData{'vTreesDirArr'},"\n";    
	print JSON_F "ploidy_ON - ",$jsonData{'ploidy_ON'},"\n";    
	print JSON_F "radio-one - ",$jsonData{'radio-one'},"\n";    
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
		return &ReadErrorLogFileStatus($curJobDir);
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
	
	my $EndFile = chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/END.txt";
	if (! -e $EndFile) {
		return 'Running';
	#}
	#
	#
	#
	#if (any { /$jobId/ } @responseLines)
	#{
	#	return 'Running';
	} else {
		
		return 'PASS';
		if (any { /$jobId/ } @response_qw_Lines)
		{
			return 'Running';
		}
		#} else {
		#	my $StatusText = &ReadFromFile("$curJobDir/END.txt", "");
		#	return $StatusText;
		#}
	}
	
 	# is any output file missing?
	#my $pathMB		= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/MB_LOG.txt";
	my $pathTree	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/Result_Tree.tre";
	#my $pathFasta	= chromEvol_CONSTS_and_Functions::RESULTS_LINK."/$jobId/SummaryDir/$jobId-concat-aligned.fasta";

	#if (! -f $pathMB)		{ return 'Failed'; }
	
	
	if (! -f $pathTree)
	{ 
		#sendFailedEmail();
		#return 'Failed'; 
		my $StatusText = &ReadFromFile("$curJobDir/SummaryDir/FinalStatus.txt", ""); 
		#return 'BlaBlaBla'; 
		return $StatusText; 
	}
	
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
	if ($errStatus eq "Running Chromevol") # Josef: make status failed if status file was last modified > 1 day
	{
		my $modify_time = (stat($errLog))[9];
		if ((($^T - $modify_time) / 86400.) > 1.)
		{
			$errStatus = "Error while running, please contact us for more details.";
		}
	}
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


