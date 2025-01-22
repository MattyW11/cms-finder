'''
Searches a series of standard URLs to check which CMS a website might be using

Todo:
Add better error handling on getSite(). Still need to pass HTTP codes are we look for HTTP 404 in the scan
Create a README and stick this on my GitHub
Add a validation method to check the initial provided site is a URL before passing it to checkFormat

CRMS to add

- Sitecore
- Wix

Examples:
python3 cms-finder.py -s example.com
python3 cms-finder.py -l websites.txt

How-it-works:
-main() passes list/site to class method: initiateScan()
- initiateScan() runs site(s) through checkFormat() that returns a formatted site
- initiateScan() then passes returned site to scanSite()
- scanSite() makes a request to the specified URL (starts with requests.getSite() so we add the correct headers)
'''
import requests
import argparse
import os
import re

#Custom argparser
class customArgParser(argparse.ArgumentParser): 

    def error(self, message): #overrides the argparse error() class with a custom message
        print(f'\n Argument Error: {message}\n')
        exit(2)

    @staticmethod #Defines the method below as static and belonging to the class, not its instance (so does not require an instance of the class be called (self))
    def parserPath(filepath):
        if os.path.exists(filepath): #os.path.exists checks if the provided dir or file exists
            return True
        else:
            return False

class scan():
    #Global variables:
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
            }
    
    def __init__(self, *args, **kwargs):
        self.site = kwargs.get('site')
        self.list = kwargs.get('list')
        self.isList = kwargs.get('isList', False)

    def checkFormat(self, url):
        """Check the provided URL(s) are formatted correctly"""
        #Remove elements from the provided address
        #Remove trailing '/'
        if url.endswith('/'):
            url = url[:-1] #remove the last character
    
        #Check if the website includes http:// or https://
        #If it is, then carry one. Otherwise, set to http://
        protocol = ('http://', 'https://')
        if url.startswith(protocol):
            pass
        else:
            url = 'http://' + url
        return url

    def getSite(self, website, allow_redirects=False):
        """Set User-Agent so site doesn't block the request. Allow global variable for sites that need redirects
        https://www.zenrows.com/blog/python-requests-user-agent#set-user-agent"""
        #Return a request using the above
        '''try:
            response = requests.get(website, allow_redirects=allow_redirects, headers=scan.headers)
            return response
        except requests.exceptions.ConnectionError as conn_err:
            conn_err: print(f'Error making request to {website}: {conn_err}') 
            return None
        except requests.exceptions.RequestException as req_err:
            req_err: print(f'Error making request to {website}: {req_err}') 
            return None'''
        try:
            return requests.get(website, allow_redirects=allow_redirects, headers=scan.headers)
        except:
            return None
            

    def checkState(self):
        """Check if site(s) are up"""
        pass

    def scanSite(self, target):
        """Scan the site against list of CMS targets"""
        print('\n')

        
        #Wrap scan inside a check to make sure getSite() doesn't return none if the site isn't available.
        siteCheck = self.getSite(target)
        if siteCheck:

            #######################################################################
            #START SCAN
            #######################################################################

            print('='*200)
            print('\n')
            print('Running scan against site:', target)
            print('\n')
            
            ###############
            #WordPress Scan
            ###############
        
            print('Running WordPress scans......')
            #Look for wp-login URL
            #Use requests.getSite allowing redirects looking for wp-login
            wpLoginScan = self.getSite(target + '/wp-login.php', allow_redirects=True)
            if wpLoginScan.status_code == 200 and 'user_login' in wpLoginScan.text and '404' not in wpLoginScan.text:
                print('[+] Detected: URL for /wp-login:', target, '/wp-login.php')
            else:
                print('[-] Not Detected: URL for /wp-login:', target + '/wp-login.php')
    
            #Use requests.getSite allowing reditect looking for wp-admin
            wpAdminScan = self.getSite(target + '/wp-admin.php', allow_redirects=True)
            if wpAdminScan.status_code == 200 and 'user_login' in wpAdminScan.text and '404' not in wpAdminScan.text:
                print('[+] Detected: URL for /wp-admin:', target, '/wp-login.php')
            else:
                print('[-] Not Detected: URL for /wp-admin:', target + '/wp-admin.php')
    
            #Look for wp-content in HTML as a common component of Wordpress sites
            wpWpContentScan = self.getSite(target)
            if 'wp-content' in wpWpContentScan.text:
                print('[+] Detected: HTML content for "wp-content" at site:', target)
            else:
                print('[-] Not Detected: HTML content for "wp-content" at site:', target)
        
            ###############
            #Joomla Scan
            ###############
            
            print('\n')
            print('Running Joomla scans......')
            
            joomlaLoginScan = self.getSite(target + '/administrator', allow_redirects=True)
            if wpLoginScan.status_code == 200 and 'user_login' in wpLoginScan.text and '404' not in wpLoginScan.text:
                print('[+] Detected: URL for /administrator:', target, '/administrator')
            else:
                print('[-] Not Detected: URL for /administrator:', target + '/administrator')

            joomlaUpdateScan = self.getSite(target + '/media/com_joomlaupdate/', allow_redirects=True)
            if wpLoginScan.status_code == 200 and 'user_login' in wpLoginScan.text and '404' not in wpLoginScan.text:
                print('[+] Detected: URL for /media/com_joomlaupdate/:', target, '/media/com_joomlaupdate/')
            else:
                print('[-] Not Detected: URL for /media/com_joomlaupdate/:', target + '/media/com_joomlaupdate/')

            joomlaMetaDataScan = self.getSite(target)
            if 'name="generator" content="Joomla' in joomlaMetaDataScan.text:
                print('[+] Detected: Metadata tag in index "name="generator" content="Joomla" at site', target)
            else:
                print('[-] Not Detected: Metadata tag in index "name="generator" content="Joomla" at site', target)

            ###############
            #Drupal Scan
            ###############

            print('\n')
            print('Running Drupal scans......')

            drupalMetaDataScan = self.getSite(target)
            if 'name="generator" content="Drupal' in drupalMetaDataScan.text:
                print('[+] Detected: Metadata tag in index "name="generator" content="Drupal" at site', target)
            else:
                print('[-] Not Detected: Metadata tag in index "name="generator" content="Drupal" at site', target)

            drupalDataSelectorScan = self.getSite(target)
            if 'data-drupal-selector' in drupalDataSelectorScan.text:
                print('[+] Detected: data Drupal selector in index "data-drupal-selector" at site', target)
            else:
                print('[-] Not Detected: data Drupal selector in index "data-drupal-selector" at site', target)

            #######################################################################
            #END SCAN
            #######################################################################

        else: #End check to make sure getSite() doesn't return none if the site isn't available
            print('The requested website is not available:', target)
        
    def initiateScan(self):
        """Initiate scan against site/list using each method"""
        if self.isList:
            #Pass each site from the list to checkFormat() then pass the returned URL to scanSite()
            try:
                with open(self.list, 'r', encoding='utf-8') as file:
                    for line in file:
                        url = line.strip() #remove space before/after line
                        if url:
                            #Logic to process each site in list through checkFormat, setAgent, and optionally checkState
                            validated_url = self.checkFormat(url)
                            self.scanSite(validated_url)
            except Exception as e:
                print('Error starting scan: ', e)
        elif not self.isList:
            try:
                #Pass the site to checkFormat() then pass the returned URL to scanSite()
                validated_url = self.checkFormat(self.site)
                self.scanSite(validated_url)
            except Exception as e:
                print('Error starting scan: ', e)
        else: #This is here to extend the program later if we want to do more than site or list from above and provide some initial validation of the above logic
            print('failed')
            sys.exit(0)


def main():
    #Define arguments
    #https://docs.python.org/3/howto/argparse.html
    parser = customArgParser(description='Find out what CMS a site is using')

    #Set either site or list as a required argument
    parser.add_argument('--version', action='version', version='cms-finder 1.0.467')
    args_group = parser.add_mutually_exclusive_group(required=True)
    args_group.add_argument('-s', '--site', help='Set the FQDN/IP to scan: example.com')
    args_group.add_argument('-l', '--list', help='File with list of websites to scan: path/to/list.txt')
    
    args = parser.parse_args()

    #Check if arguments is provided (argparser looks for the long option denoted by '--', and so include the short option denoted by '-')
    if args.site:
        initiate = scan(
            site = args.site, 
            isList = False, 
        )
    #Check if list path and filename exist
    elif args.list and not parser.parserPath(args.list):
        parser.error('The filename or path provided does not exist')
    elif args.list:
        initiate = scan(
            list=args.list, 
            isList=True, 
        )

    initiate.initiateScan()

##Run main()
if __name__ == '__main__':
    main()