<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
    <html>
    <head>
        <title>Checkbox Report</title>
        <link rel="stylesheet" type="text/css" href="file:///usr/share/checkbox/report/checkbox.css" media="all" />
    </head>
    <body>
    <h1>Checkbox Report</h1>
    <h2 id="toc">Table Of Contents</h2>
    <ol>
        <li><a href="#summary">Summary</a></li>
        <li>Hardware
        <ul>
            <li><a href="#hal">HAL</a></li>
            <li><a href="#processors">Processors</a></li>
            <li><a href="#dmi">DMI</a></li>
            <li><a href="#lspci">PCI</a></li>
        </ul></li>
        <li>Software
        <ul>
            <li><a href="#packages">Packages</a></li>
            <li><a href="#lsb_release">LSB</a></li>
        </ul></li>
        <li><a href="#questions">Questions</a></li>
     </ol>
    <xsl:apply-templates select=".//summary" />
    <xsl:apply-templates select=".//hardware/hal" />
    <xsl:apply-templates select=".//hardware/processors" />
    <xsl:apply-templates select=".//hardware/dmi" />
    <xsl:apply-templates select=".//hardware/lspci" />
    <xsl:apply-templates select=".//software/packages" />
    <xsl:apply-templates select=".//software/lsb_release" />
    <xsl:apply-templates select=".//questions" />
    </body>
    </html>
</xsl:template>

<xsl:template match="summary">
    <h2 id="summary">Summary</h2>
    <p>This report was created using <xsl:value-of select="client/@name" /> <xsl:text> </xsl:text><xsl:value-of select="client/@version" /> on <xsl:value-of select="date_created/@value" />, on <xsl:value-of select="distribution/@value" /><xsl:text> </xsl:text><xsl:value-of select="distroseries/@value" /> (<xsl:value-of select="architecture/@value" />).</p>
    <p>You can view other reports for this system <a href="https://launchpad.net/+hwdb/+submission/{system_id/@value}">here</a>.</p>
</xsl:template>

<xsl:template match="hardware/hal">
    <h2 id="hal">HAL</h2>
    <xsl:for-each select="device">
        <h3><xsl:value-of select='property[@name="info.product"]' /></h3>
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
    </xsl:for-each>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="hardware/processors">
    <h2 id="processors">Processors</h2>
    <xsl:for-each select="processor">
        <h3><xsl:value-of select='@name' /></h3>
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
    </xsl:for-each>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="hardware/dmi">
    <h2 id="dmi">DMI</h2>
    <pre><xsl:value-of select="." /></pre>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="hardware/lspci">
    <h2 id="lspci">PCI</h2>
    <pre><xsl:value-of select="." /></pre>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="software/packages">
    <h2 id="packages">Packages</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Version</th>
        </tr>
        <xsl:for-each select="package">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td><xsl:value-of select="property" /></td>
            </tr>
        </xsl:for-each>
    </table>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="software/lsb_release">
    <h2 id="lsb_release">LSB</h2>
    <table>
        <xsl:for-each select="property">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td><xsl:value-of select="." /></td>
            </tr>
        </xsl:for-each>
    </table>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

<xsl:template match="questions">
    <h2 id="questions">Questions</h2>
        <table>
        <tr>
            <th>Name</th>
            <th>Answer</th>
            <th>Comment</th>
        </tr>
        <xsl:for-each select="question">
            <tr>
                <td class="label"><xsl:value-of select="@name" /></td>
                <td><xsl:value-of select="answer" /></td>
                <td><xsl:value-of select="comment" /></td>
            </tr>
        </xsl:for-each>
    </table>
    <p class="navigation"><a href="#toc">Back to Table of Contents</a></p>
</xsl:template>

</xsl:stylesheet>
