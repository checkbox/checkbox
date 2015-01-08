<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
    <html>
    <head>
        <title>System Testing Report</title>
        <link rel="stylesheet" type="text/css" href="${PLAINBOX_ASSETS}/report/styles.css" />
        <script type="text/javascript" src="${PLAINBOX_ASSETS}/report/checkbox.js">
        </script>
    </head>
    <body>
        <!-- Quick and dirty preload to have disclosure triangle images cached -->
        <img src="${PLAINBOX_ASSETS}/report/images/open.png" style="display: none;" /><img src="${PLAINBOX_ASSETS}/report/images/closed.png" style="display: none;" />
        <div id="container">
            <div id="container-inner">

                <div id="title">
                    <h1>System Testing<span class="grey"> Report</span></h1>
                </div>
                <div id="content" class="clearfix">
                    <xsl:apply-templates select=".//summary" />
                </div>
                <div id="content" class="clearfix">
                    <h2>Hardware Information</h2>
                    <xsl:apply-templates select=".//hardware/dmi" />
                    <xsl:apply-templates select=".//hardware/sysfs-attributes" />
                    <xsl:apply-templates select=".//hardware/processors" />
                    <xsl:apply-templates select=".//hardware/lspci" />
                </div>
                <div id="content" class="clearfix">
                    <h2>Software Information</h2>
                    <xsl:apply-templates select=".//software/packages" />
                    <xsl:apply-templates select=".//software/lsbrelease" />
                    <xsl:apply-templates select=".//software/requirements"/>
                </div>
                <div id="content" class="clearfix">
                    <h2>Tests Performed</h2>
                    <xsl:apply-templates select=".//questions" />
                </div>
                <div id="content" class="clearfix">
                    <h2>Log Files and Environment Information</h2>
                    <xsl:apply-templates select=".//context" />
                </div>
            </div>
        </div>
    </body>
    </html>
</xsl:template>

<xsl:template match="summary">
    <p>
     This report was created using <xsl:value-of select="client/@name" /> <xsl:text> </xsl:text><xsl:value-of select="client/@version" /> on 
     <xsl:value-of select="date_created/@value" />
    </p>
</xsl:template>

<xsl:template match="hardware/udev">
    <div onClick="showHide('udev');">
        <h3 id="udev"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />Devices detected in the system (udev)</h3>
    </div>
    <div class="data" id="udev-contents">
        <pre><xsl:value-of select="." /></pre>
    </div>
</xsl:template>

<xsl:template match="hardware/dmi">
    <span onClick="showHide('dmi');"><h3 id="dmi"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />Desktop Management Interface information</h3></span>
    <div class="data" id="dmi-contents" style="overflow: auto;">
        <pre><xsl:value-of select="." /></pre>
    </div>
</xsl:template>

<xsl:template match="hardware/sysfs-attributes">
    <span onClick="showHide('sysfs-attributes');"><h3 id="sysfs-attributes"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />sysfs-attributes</h3></span>
    <div class="data" id="sysfs-attributes-contents">
        <pre><xsl:value-of select="." /></pre>
    </div>
</xsl:template>

<xsl:template match="hardware/processors">
    <span onClick="showHide('processors');"><h3 id="processors"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />Processors</h3></span>
    <div class="data" id="processors-contents">
    <xsl:for-each select="processor">
        <h3><u>Processor <xsl:value-of select='@name' /></u></h3>
        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
        <xsl:for-each select="property">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td class="property"><xsl:value-of select="." /></td>
            </tr>
        </xsl:for-each>
        </table>
	<br />
    </xsl:for-each>
    </div>
</xsl:template>

<xsl:template match="software/lsbrelease">
    <h3 id="lsbrelease">Installed version of Ubuntu</h3>
    <table>
        <xsl:for-each select="property">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td><xsl:value-of select="." /></td>
            </tr>
        </xsl:for-each>
    </table>
</xsl:template>
<xsl:template match="software/packages">
    <span onClick="showHide('packages');"><h3 id="packages"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />Packages Installed</h3></span>
    <div class="data" id="packages-contents">
    <table>
        <tr>
            <th>Name</th>
            <th>Description</th>
        </tr>
        <xsl:for-each select="package">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td><xsl:value-of select="property" /></td>
            </tr>
        </xsl:for-each>
    </table>
    </div>
</xsl:template>
<xsl:template match="software/requirements">
    <span onClick="showHide('requirements');"><h3 id="requirements"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />Requirements</h3></span>
    <div class="data" id="requirements-contents">
    <table>
        <xsl:for-each select="requirement">
            <tr>
                <td>
                 <a href="{.}"><xsl:value-of select="@name" /></a>
                </td>
            </tr>
        </xsl:for-each>
    </table>
    </div>
</xsl:template>

<xsl:template match="questions">
    <h3 id="questions">Tests</h3>
        <table style="width: 700px">
        <tr>
            <th> </th>
            <th>Name</th>
            <th style="width: 15em;">Result</th>
            <th>Comment</th>
        </tr>
        <xsl:for-each select="question">
            <tr>
                <xsl:choose>
                    <xsl:when test="normalize-space(answer) = 'fail'">
                        <td><img class='resultimg' src='${PLAINBOX_ASSETS}/report/images/fail.png' /></td>
                        <td class="label"><xsl:value-of select="@name" /></td>
                        <td style='background-color: #DC3912'>FAILED</td>
                        <td><xsl:value-of select="comment" /></td>
                    </xsl:when>
                    <xsl:when test="normalize-space(answer) = 'pass'">
                        <td><img class='resultimg' src='${PLAINBOX_ASSETS}/report/images/pass.png' /></td>
                        <td class="label"><xsl:value-of select="@name" /></td>
                        <td style='background-color: #6AA84F'>PASSED</td>
                        <td><xsl:value-of select="comment" /></td>
                    </xsl:when>
                    <xsl:when test="normalize-space(answer) = 'unsupported'">
                        <td></td>
                        <td class="label"><xsl:value-of select="@name" /></td>
                        <td style='background-color: #FF9900'>not required on this system</td>
                        <td><xsl:value-of select="comment" /></td>
                    </xsl:when>
                    <xsl:when test="normalize-space(answer) = 'skip'">
                        <td><img class='resultimg' src='${PLAINBOX_ASSETS}/report/images/skip.png' /></td>
                        <td class="label"><xsl:value-of select="@name" /></td>
                        <td style='background-color: #FF9900'>SKIPPED</td>
                        <td><xsl:value-of select="comment" /></td>
                    </xsl:when>
                    <xsl:otherwise>
                        <td></td>
                        <td class="label"><xsl:value-of select="@name" /></td>
                        <td><xsl:value-of select="answer" /></td>
                        <td><xsl:value-of select="comment" /></td>
                    </xsl:otherwise>
                </xsl:choose>
            </tr>
        </xsl:for-each>
    </table>
</xsl:template>

<xsl:template match="context">
    <div id="packages-contents">    
    <xsl:for-each select="info">
	<span onClick="showHide('{generate-id(.)}');"><h3 id="{generate-id(.)}"><img class="disclosureimg" src="${PLAINBOX_ASSETS}/report/images/closed.png" />
        <xsl:value-of select="@command" /></h3></span>
	<div class="data" id="{generate-id(.)}-contents" style="overflow: auto;">
	        <pre><xsl:value-of select="." /></pre>
	</div>
    </xsl:for-each>
    </div>
</xsl:template>

</xsl:stylesheet>
