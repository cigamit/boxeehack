import os
import xbmc, xbmcgui
import ConfigParser

available_providers = ['Addic7ed', 'BierDopje', 'OpenSubtitles', 'SubsWiki', 'Subtitulos']

# Read file contents into a string
def file_get_contents(filename):
    if os.path.exists(filename):
        fp = open(filename, "r")
        content = fp.read()
        fp.close()
        return content
    return ""

# Write string back to a file
def file_put_contents(filename, content):
    fp = open(filename, "w")
    fp.write(content)
    fp.close()

# Set some default values for the subtitles handling
def register_defaults():
    subtitle_provider("get", "default")
    subtitle_provider("get", "tv")
    subtitle_provider("get", "movie")
    xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,%s)" % get_subtitles_language_filter() )
    xbmc.executebuiltin("Skin.SetString(subtitles-plugin,%s)" % get_subtitles_enabled() ) 

# Set the password for the telnet functionality    
def set_telnet_password():
    passwd = file_get_contents("/data/etc/passwd")
    kb = xbmc.Keyboard('default', 'heading', True)
    kb.setDefault(passwd) # optional
    kb.setHeading('Enter telnet password') # optional
    kb.setHiddenInput(True) # optional
    kb.doModal()
    if kb.isConfirmed():
        passwd = kb.getText()

    if passwd == "":
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Telnet', 'The telnet password must not be empty.')
    else:
        file_put_contents("/data/etc/passwd", passwd)    

# Determine whether subtitle functionality is enabled/enabled
def get_subtitles_enabled():
    subtitles = file_get_contents("/data/etc/.subtitles_enabled")
    if subtitles == "":
        subtitles = "0"
    return subtitles

def get_subtitles_language_filter():
	config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })
        if os.path.exists("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini"):
      		config.read("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini")
	langs_config = config.get("DEFAULT", "lang")
	if(langs_config.strip() == "" or langs_config == "All"):
		return "0"
	else:
		return "1"	

# Enable/disable the subtitle functionality
def toggle_subtitles(mode):

	if(mode == "all"):
    		subtitles = get_subtitles_enabled()

		if subtitles == "1":
        		subtitles = "0"
    		else:
        		subtitles = "1"

    		file_put_contents("/data/etc/.subtitles_enabled", subtitles)
    		os.system("sh /data/hack/subtitles.sh")
    		xbmc.executebuiltin("Skin.SetString(subtitles-plugin,%s)" % subtitles )    
	if(mode == "language"):
		if(get_subtitles_language_filter() == "0"):
			xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,1)" )		
		else:
			config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })
                	if os.path.exists("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini"):
                        	config.read("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini")
			config.set("DEFAULT", "lang", "All")
			
			if os.path.exists("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini"):
                        	configfile = open("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini", "w")
                        	config.write(configfile)
                        	configfile.close()
			xbmc.executebuiltin("Skin.SetString(subtitles-plugin-language,0)" )

# Edit the subtitle providers
def subtitle_provider(method, section, provider=None):
    config = ConfigParser.SafeConfigParser({"lang": "All", "plugins" : "BierDopje,OpenSubtitles", "tvplugins" : "BierDopje,OpenSubtitles", "movieplugins" : "OpenSubtitles" })

    if os.path.exists("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini"):
    	config.read("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini")

    plugins = config.get("DEFAULT", "plugins")	
    plugin_section = "default"
    config_section = "plugins"

    if section == "tv":
        plugins = config.get("DEFAULT", "tvplugins")
        plugin_section = "tv"
        config_section = "tvplugins"

    if section == "movie":
        plugins = config.get("DEFAULT", "movieplugins")
        plugin_section = "movie"
        config_section = "movieplugins"
    
    enabled_providers = plugins.split(',')
    if method == "get":
        if provider != None:
            if provider in enabled_providers:
                return 1
            else:
                return 0

        for checkprovider in available_providers:
            result = 0
            if checkprovider in enabled_providers:
                result = 1
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, checkprovider, result))

    if method == "set":
        provider_status = 1
        if provider in enabled_providers:
            provider_status = 0

        if provider_status == 1:
            enabled_providers.append(provider)
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, provider, 1))
        else:
            enabled_providers.remove(provider)
            xbmc.executebuiltin("Skin.SetString(subtitles-plugin-%s-%s,%s)" % (plugin_section, provider, 0))
        config.set("DEFAULT", config_section, ",".join(enabled_providers).strip(','))
        if os.path.exists("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini"):
            configfile = open("/data/hack/boxee/scripts/OpenSubtitles/resources/lib/config.ini", "w")
            config.write(configfile)
            configfile.close()

# Check for newer version
def check_new_version():
    import urllib2
    u = urllib2.urlopen('https://raw.github.com/boxeehacks/boxeehack/master/hack/version')
    version_remote = "%s" % u.read()
    version_local = file_get_contents("/data/hack/version")

    version_remote_parts = version_remote.split(".")
    version_local_parts = version_local.split(".")

    hasnew = 0
    if version_remote_parts[0] > version_local_parts[0]:
        hasnew = 1
    elif version_remote_parts[0] == version_local_parts[0]:
        if version_remote_parts[1] > version_local_parts[1]:
            hasnew = 1
        elif version_remote_parts[1] == version_local_parts[1]:
            if version_remote_parts[2] > version_local_parts[2]:
                hasnew = 1

    dialog = xbmcgui.Dialog()
    if hasnew:
        dialog.ok("BoxeeHack Version", "A new version of BoxeeHack is available. Upgrade to %s" % (version_remote))
    else:
        dialog.ok("BoxeeHack Version", "Your BoxeeHack version is up to date.")

if (__name__ == "__main__"):
    command = sys.argv[1]

    if command == "telnet": set_telnet_password()
    if command == "subtitles": toggle_subtitles(sys.argv[2])
    if command == "version": check_new_version()
    if command == "defaults": register_defaults()
    if command == "subtitles-provider":
        subtitle_provider("set", sys.argv[2], sys.argv[3])
