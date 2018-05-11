
#include "wazuh_modules/wmodules.h"
#include <stdio.h>

static const char *XML_DISABLED = "disabled";
static const char *XML_BINPATH = "binpath";
static const char *XML_LOGPATH = "logpath";
static const char *XML_CONFIGPATH = "configpath";
static const char *XML_PACK = "pack";
static const char *XML_PACKNAME = "name";

//Función de lectura
int wm_osquery_monitor_read(xml_node **nodes, wmodule *module)
{
    unsigned int i;
    unsigned int pack_i = 0;
    wm_osquery_monitor_t *osquery_monitor;

    os_calloc(1, sizeof(wm_osquery_monitor_t), osquery_monitor);
    os_strdup("/usr/bin", osquery_monitor->bin_path);
    os_strdup("/var/log/osquery/osqueryd.results.log", osquery_monitor->log_path);
    os_strdup("/etc/osquery/osquery.conf", osquery_monitor->config_path);
    os_calloc(1, sizeof(wm_osquery_pack_t *), osquery_monitor->packs);
    osquery_monitor->disable = 0;
    module->context = &WM_OSQUERYMONITOR_CONTEXT;
    module->data = osquery_monitor;

    for(i = 0; nodes[i]; i++)
    {
        if(!nodes[i]->element)
        {
            merror(XML_ELEMNULL);
            return OS_INVALID;
        }
        else if (!strcmp(nodes[i]->element, XML_DISABLED))
        {
            if (!strcmp(nodes[i]->content, "yes"))
                osquery_monitor->disable = 1;
            else if (!strcmp(nodes[i]->content, "no"))
            {
                osquery_monitor->disable = 0;
            }
            else
            {
                merror("Invalid content for tag '%s' at module '%s'.", XML_DISABLED, WM_OSQUERYMONITOR_CONTEXT.name);
                return OS_INVALID;
            }
        }
        else if(!strcmp(nodes[i]->element, XML_BINPATH))
        {
            free(osquery_monitor->bin_path);
            osquery_monitor->bin_path = strdup(nodes[i]->content);
        }
        else if(!strcmp(nodes[i]->element, XML_LOGPATH))
        {
            free(osquery_monitor->log_path);
            osquery_monitor->log_path = strdup(nodes[i]->content);
            mdebug2("Logpath read: %s", osquery_monitor->log_path);
        }
        else if(!strcmp(nodes[i]->element, XML_CONFIGPATH))
        {
            free(osquery_monitor->config_path);
            osquery_monitor->config_path = strdup(nodes[i]->content);
            mdebug2("configPath Readed: %s", osquery_monitor->config_path);
        } else if (!strcmp(nodes[i]->element, XML_PACK)) {
            wm_osquery_pack_t * pack;

            if (!(nodes[i]->attributes && *nodes[i]->attributes) || strcmp(*nodes[i]->attributes, XML_PACKNAME)) {
                merror("No such attribute '%s' in osquery element <%s>", XML_PACKNAME, XML_PACK);
                return OS_INVALID;
            }

            os_malloc(sizeof(wm_osquery_pack_t), pack);
            os_strdup(*nodes[i]->values, pack->name);
            os_strdup(nodes[i]->content, pack->path);
            os_realloc(osquery_monitor->packs, (pack_i + 2) * sizeof(wm_osquery_pack_t *), osquery_monitor->packs);
            osquery_monitor->packs[pack_i] = pack;
            osquery_monitor->packs[++pack_i] = NULL;
        }

    }
    return 0;
}
