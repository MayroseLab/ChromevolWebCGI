#!/usr/bin/perl -w

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use File::Path; 
use File::Slurp;

use lib "../";
use lib "/bioseq/chromEvol";
#use lib "/bioseq/chromEvol/webServer_files";

use chromEvol_CONSTS_and_Functions;

# this command limits the size of the uploded file
my $maxMB = 100; 
$CGI::POST_MAX = 1024 * 1000 * $maxMB;

my $safe_filename_characters = "a-zA-Z0-9_.-";
my $jobId 		= $^T;
	
my $cromevol_scripts_pth = chromEvol_CONSTS_and_Functions::CHROMEVOL_SCRIPTS_PATH;

my $curJobdir 		= chromEvol_CONSTS_and_Functions::RESULTS_DIR_ABSOLUTE_PATH."/$jobId";
#my $curJobdir 		= chromEvol_CONSTS_and_Functions::RESULTS_DIR_ABSOLUTE_PATH.$jobId;
my $log 			= "$curJobdir/".chromEvol_CONSTS_and_Functions::LOG_FILE;
my $fnameParamsTxt	= "$curJobdir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_TXT;
my $fnameParamsHtml	= "$curJobdir/".chromEvol_CONSTS_and_Functions::FILENAME_PARAMS_HTML;
my $fnameEmail		= "$curJobdir/".chromEvol_CONSTS_and_Functions::FILENAME_EMAIL;
my $errLog 			= "$curJobdir/".chromEvol_CONSTS_and_Functions::ERROR_STATUS_LOG_FILE;
my $chromevol_param_templates = chromEvol_CONSTS_and_Functions::CHROMEVOL_PARAM_PATH;
my $chromevol_exe_path = chromEvol_CONSTS_and_Functions::CHROMEVOL_EXE_PATH;

my $query = new CGI;

# getting inputs from user
# Global parameters
my $rooted					= $query->param("Outgroup_Flag");
my $MSA_Software			= $query->param("MSA_Software");
my $FilterMSA_Method		= $query->param("FilterMSA_Method");
my $Tree_Method				= $query->param("Tree_Method");
my $OriginJobID 			= $query->param("OriginJobID");
my $countsType 				= $query->param("countsType");
my $rerun 					= ( $OriginJobID eq "None" ? "Off" : "On. Original run ID: $OriginJobID" );


#Chromevol parameters from user:
my $fTreeFile 			= "$curJobdir/TreesFile.txt";
my $fUserTreesFile		= $query->param("TreeFile_txt");
&WriteToFile($fTreeFile, $fUserTreesFile);

my $fCountsFile 			= "$curJobdir/CountsFile.txt";
my $fUserCountsFile		= $query->param("CountsFile_txt");
&WriteToFile($fCountsFile, $fUserCountsFile);



my $runModels_param = $query->param("ModelSelect");


##my $NodeDateInput			= $query->param("files");
my $fnameNodeDate 			= "$curJobdir/NodeDate.txt";
my $NodeDateInputFile		= $query->param("NodeDateInputFile");
#
&WriteToFile($fnameNodeDate, $NodeDateInputFile);

my $inputFile				= $query->param("inputFile");
my $fnameUserInput 			= "$curJobdir/userInput.txt";
# copy the seq from textarea to file
my $inputText				= $query->param("inputText");

# patch for rerun: always create the file userInput.txt . case user uploads a file: userInput.txt will be overwritten. case rerun: userInput.txt will be empry. 
#if (!($inputText eq ""))
{
	&WriteToFile( $fnameUserInput, $inputText);
}

#Load newick constraint tree to file:
my $fconstraintTreeFile 			= "$curJobdir/ConstraintTree_user.txt";
my $constraintTreeInput				= $query->param("ConstraintNewick");
&WriteToFile( $fconstraintTreeFile, $constraintTreeInput);

my $fconstraintUserIDFile 			= "$curJobdir/ConstraintTaxIdList_user.txt";
my $constraintTaxIDInput				= $query->param("ConstraintTaxaList");
&WriteToFile( $fconstraintUserIDFile, $constraintTaxIDInput);


my $email_to_address		= $query->param("inputEmail");
my $jobTitle				= $query->param("jobTitle");
my $date					= $query->param("date");


=pod

# these will be displayed on results.html:
&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Submitted at:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$date."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Job title:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$jobTitle."&nbsp</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Outgroup selection:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$rooted."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">MSA software:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$MSA_Software."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">MSA filter:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$FilterMSA_Method."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Phylogenetic tree method:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$Tree_Method."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Rerun:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$rerun."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

&WriteToFile( $fnameParamsHtml, "<div class=\".row\">");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-3 col-lg-3 params\">Email:</div>");
&WriteToFile( $fnameParamsHtml, "<div class=\"col-md-9 col-lg-9 params\">".$email_to_address."</div><br>");
&WriteToFile( $fnameParamsHtml, "</div>");

=cut



#&WriteToFile( $fnameParamsHtml, "<h4>Job title: <i>".$jobTitle."</i></h4><h4>Rooted: <i>".$rooted."</i></h4><h4>MSA software: <i>".$MSA_Software."</i></h4><h4>MSA Filter: <i>".$FilterMSA_Method."</i></h4><h4>Phylogenetic Tree Method: <i>".$Tree_Method."</i></h4><h4>Rerun: <i>".$rerun."</i></h4><h4>Email: <i>".$email_to_address."</i></h4>");
&WriteToFile( $fnameEmail, $email_to_address); # to be read by result cgi once run ends

# print all params to params.txt file
my @names = $query->param;
foreach my $name ( @names ) 
{
	# dont print field inputText to params.txt
	if ($name eq "inputText" or $name eq "TreeFile_txt" or $name eq "CountsFile_txt")
	{
		next;
	}
	WriteToFile($fnameParamsTxt, $name . ":" . $query->param($name));
	if ($name eq "NumberOfTrees"){
		my @dir_num = (1..$query->param($name));
		my $AllTreesPaths = "TreesDirArr:";
		foreach my $treeNum (@dir_num){
			my $treePath = $curJobdir . "/ChromEvol_Tree_" . $treeNum;
			$AllTreesPaths = $AllTreesPaths . "$treePath" . ",";
		}
		WriteToFile($fnameParamsTxt, $AllTreesPaths);
	}
}

# creating cur job directory
mkpath($curJobdir);

#if ( !$inputFile )
#{
#	print $query->header ( );
#	print "There was a problem uploading your structure zip (try a smaller file).";
#	exit;
#} 

# checking filename for invalid characters
if ($inputFile)
{
	my ( $name, $path, $extension ) = fileparse ( $inputFile, '\..*' );
	$inputFile = $name . $extension;
	$inputFile =~ tr/ /_/;
	$inputFile =~ s/[^$safe_filename_characters]//g;

	if ( $inputFile =~ /^([$safe_filename_characters]+)$/ )
	{
		$inputFile = $1;
	}
	else
	{
		die "Filename contains invalid characters";
	}
	
	# uploading file to job directory
	my $upload_filehandle = $query->upload("inputFile");
	my $serverLocation = "$curJobdir/$inputFile";
	open ( UPLOADFILE, ">$serverLocation" ) or die "$!";
	binmode UPLOADFILE;

	while ( <$upload_filehandle> )
	{
		print UPLOADFILE;

	}

	close UPLOADFILE;
	rename $serverLocation, $fnameUserInput;
}


# building perl script command
my $serverName 		= chromEvol_CONSTS_and_Functions::SERVER_NAME;
my $pythonModule	= chromEvol_CONSTS_and_Functions::PYTHON_MODULE_TO_LOAD;
my $perlModule		= chromEvol_CONSTS_and_Functions::PERL_MODULE_TO_LOAD;



my $pid = fork();
if( $pid == 0 )
{
	# this code runs async
	open STDIN,  '<', '/dev/null';
    #open STDOUT, '>', $validationLog; # point to /dev/null or to a log file
    #open STDERR, '>&STDOUT';
    
	# logging user request
	use POSIX qw(strftime);
	my $date = strftime('%F %H:%M:%S', localtime);
	my $logPath = chromEvol_CONSTS_and_Functions::LOG_DIR_ABSOLUTE_PATH; 
	$logPath = $logPath.chromEvol_CONSTS_and_Functions::MAIN_PIPELINE_LOG;
	&WriteToFile( $logPath, "$email_to_address\t$date\t$jobId");

        #creating the PIP control file for chromevol:
	my $pip_chromevol_file = "$curJobdir/PIP_control";
	#open(PIP_FILE,">$pip_chromevol_file");
	#print PIP_FILE '_treesFile ', "$fTreeFile", "\n"; 
	#print PIP_FILE '_dataFile ', "$fCountsFile", "\n"; 
	#print PIP_FILE '_outDir ' , "$curJobdir",'/chromevol_out',"\n";
	#print PIP_FILE  '_name ' , "$jobId","\n";
	##print PIP_FILE  '_paramTemplates /groups/itay_mayrose/michaldrori/MD_ChromEvol/power_PARAM_templates/' ,"\n";
	##print PIP_FILE  '_chromevolExe /groups/itay_mayrose/michaldrori/scripts/chromEvol.exe' ,"\n";
    #
	#print PIP_FILE  '_paramTemplates ' , "$chromevol_param_templates","\n";
	#print PIP_FILE  '_chromevolExe ' , "$chromevol_exe_path",'/chromEvol.exe',"\n";
	#print PIP_FILE  '_cpusNum 1',"\n";
	#print PIP_FILE '_runModels ', "$models_string", "\n";
	#close (PIP_FILE);
		
	#creating shell script file for lecs2
	my $qsub_script = "$curJobdir/qsub.sh";
	open (QSUB_SH,">$qsub_script");
	  
	print QSUB_SH "#!/bin/bash\n";
	print QSUB_SH '#PBS -N ', "$serverName"."_$jobId","\n";
	#print QSUB_SH '#PBS -j oe',"\n";
	print QSUB_SH '#PBS -r y',"\n";
	print QSUB_SH '#PBS -q lifesciweb',"\n";
	print QSUB_SH '#PBS -v PBS_O_SHELL=bash,PBS_ENVIRONMENT=PBS_BATCH',"\n";
	
	print QSUB_SH '#PBS -e ', "$curJobdir", '/',"\n";
	print QSUB_SH '#PBS -o ', "$curJobdir", '/',"\n";
	print QSUB_SH 'module load ', "$perlModule","\n";
	print QSUB_SH 'module load ', "$pythonModule","\n";
	
	#my $cmd .= "python /bioseq/oneTwoTree/OneTwoTree.py $fnameUserInput $curJobdir $jobId;";
	#my $cmd .= "perl $cromevol_scripts_pth/step1_preparation.pl $curJobdir/PIP_control";
	#	python /bioseq/chromEvol/Chromevol_scripts/Chromevol_server.py /bioseq/data/results/chromEvol/1548663671 /bioseq/data/results/chromEvol/1548663671/tree_100 /bioseq/data/results/chromEvol/1548663671/1548663671.counts
	
	#my $cmd .= "python $cromevol_scripts_pth/Chromevol_server.py $curJobdir $curJobdir/TreeFile $curJobdir/countsFile";
	my $cmd .= "python $cromevol_scripts_pth/ChromEvol_getCCDBCounts.py $fTreeFile $curJobdir 0 $countsType";
 
	print QSUB_SH "$cmd\n";
	close (QSUB_SH);
    
   
	my $qsubCmd =  'ssh bioseq@powerlogin qsub '."$qsub_script";


	
	# this is not done here, but by OTT at end of run
	#my $cmdEmail = "perl /bioseq/$serverName/sendLastEmail.pl --toEmail $email_to_address --id $jobId;";
	#print QSUB_SH "$cmdEmail\n";
	
	
	#my $qsubCmd =  'ssh bioseq@jekyl qsub '."$qsub_script";
	#my $qsubCmd =  'ssh bioseq@lecs2 qsub '."$qsub_script";
	
	my 	$qsubJobNum = "NONE";
	my $ans = `$qsubCmd`;
	if ($ans =~ /(\d+)/)
	{
		$qsubJobNum = $1;
	}
	
	write_file("$curJobdir/".chromEvol_CONSTS_and_Functions::QSUB_JOB_NUM_FILE, $qsubJobNum);
	#&WriteToFileWithTimeStamp($log, "Job $jobId was submitted to queue.");
	
	exit 0;
}


# redirecting client to results page
my $redirectedURL = chromEvol_CONSTS_and_Functions::RESULTS_COUNTS_PAGE_URL."?jobId=";
$redirectedURL = $redirectedURL.$jobId;
$redirectedURL .= "&jobTitle=".$jobTitle;

print $query->redirect($redirectedURL);
