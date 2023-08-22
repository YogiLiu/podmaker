<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/rss">
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <link rel="icon"
                      href="data:;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABVklEQVQ4T33SjTEEQRAFYBcBMjgRIAInAkRgRYAInAyIwMqACKwIEIHLwGXA+7ZmquZ+Sle9mp3pfq/fzvRkZzP2cnQdzApUfAYvwWOwbCmTNf559k/BV9AHi5KfZu2Cw+CqiI2pVkDHt1KAjHASIOv+HNQGp/keWgG2PwIWJbggjiiI7QaIGvnF42BZHSiYl27+F5zp+Bu8Bn3A0UGwKPV9FRhyUKFwGjyUTllG+wQrUf5Ig1aAg1khK9a5DbXEiWg21rcCkpSJgCKWxXs5cyd+j0jXCrAriCCy570V1XPrd3ARuBtxUx3MsqE+LSLIhC5LoTtQI49chYZ2DhAkbkuhvaer4QnZ55YQwZVBMgtVxLT9NGSf+4H58IzI40ivjzKRPlgE7qFeotEmrnNXydsEalOFrJ6VA6+ASHgl1h20yXk2d+XgPqv9RvwnwIVLE25+2CbwB4IRVBGThzfSAAAAAElFTkSuQmCC"/>
                <title>
                    <xsl:value-of select="/rss/channel/title"/>
                    - Podmaker
                </title>
                <meta charset="UTF-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
                <link rel="stylesheet"
                      href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"/>
                <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
            </head>
            <body style="display: flex; flex-direction: column; min-height: 100vh;">
                <header>
                    <nav>
                        <div class="nav-wrapper container">
                            <a href="#" class="brand-logo" target="_blank">
                                <xsl:if test="channel/link">
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="channel/link"/>
                                    </xsl:attribute>
                                </xsl:if>
                                <i class="material-icons">rss_feed</i>
                                <xsl:value-of select="channel/title"/>
                            </a>
                        </div>
                    </nav>
                </header>
                <main style="flex-grow: 1;margin: 60px auto;" class="container">
                    <xsl:choose>
                        <xsl:when test="channel/itunes:image">
                            <div>
                                <img alt="cover" src="" height="150"
                                     style="margin: 0 auto; display: block; border-radius: 10%;">
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="channel/itunes:image/@href"/>
                                    </xsl:attribute>
                                </img>
                            </div>
                        </xsl:when>
                        <xsl:when test="channel/image">
                            <div>
                                <img alt="cover" src="" height="150"
                                     style="margin: 0 auto; display: block; border-radius: 10%;">
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="channel/image/url"/>
                                    </xsl:attribute>
                                </img>
                            </div>
                        </xsl:when>
                    </xsl:choose>
                    <xsl:choose>
                        <xsl:when test="channel/itunes:summary">
                            <p style="text-align: center;">
                                <xsl:value-of select="channel/itunes:summary"/>
                            </p>
                        </xsl:when>
                        <xsl:when test="channel/description">
                            <p style="text-align: center;">
                                <xsl:value-of select="channel/description"/>
                            </p>
                        </xsl:when>
                    </xsl:choose>
                    <xsl:if test="channel/itunes:author">
                        <p style="text-align: center;">
                            <a href="#" target="_blank" class="grey-text">
                                <xsl:if test="channel/link">
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="channel/link"/>
                                    </xsl:attribute>
                                </xsl:if>
                                @
                                <xsl:value-of select="channel/itunes:author"/>
                            </a>
                        </p>
                    </xsl:if>
                    <div class="row">
                        <xsl:for-each select="channel/item">
                            <xsl:sort select="position()" data-type="number" order="descending"/>
                            <div class="col s12 podcast-item" style="display: none;">
                                <div class="card">
                                    <div class="card-image">
                                        <xsl:if test="itunes:image">
                                            <img>
                                                <xsl:attribute name="src">
                                                    <xsl:value-of select="itunes:image/@href"/>
                                                </xsl:attribute>
                                            </img>
                                        </xsl:if>
                                        <a target="_blank">
                                            <xsl:if test="link">
                                                <xsl:attribute name="href">
                                                    <xsl:value-of select="link"/>
                                                </xsl:attribute>
                                            </xsl:if>
                                            <h2 class="card-title">
                                                <xsl:value-of select="title"/>
                                            </h2>
                                        </a>
                                    </div>
                                    <xsl:if test="description">
                                        <div class="card-content">
                                            <p>
                                                <xsl:value-of select="description"/>
                                            </p>
                                        </div>
                                    </xsl:if>
                                    <div class="card-action">
                                        <audio controls="controls" style="width: 100%;">
                                            <xsl:attribute name="src">
                                                <xsl:value-of select="enclosure/@url"/>
                                            </xsl:attribute>
                                        </audio>
                                    </div>
                                </div>
                            </div>
                        </xsl:for-each>
                    </div>
                    <xsl:if test="channel/item">
                        <ul class="pagination" style="text-align: center">
                            <li class="disabled prev">
                                <a style="cursor: pointer;">
                                    <i class="material-icons">chevron_left</i>
                                </a>
                            </li>
                            <li class="waves-effect next">
                                <a style="cursor: pointer;">
                                    <i class="material-icons">chevron_right</i>
                                </a>
                            </li>
                        </ul>
                    </xsl:if>
                </main>
                <footer class="page-footer">
                    <div class="container">
                        <div class="row">
                            <div class="col l6 s12">
                                <h5 class="white-text">Podmaker</h5>
                                <p class="grey-text text-lighten-4 right">
                                    This is a Podcast RSS Feed generated by
                                    <a class="grey-text text-lighten-4" href="https://github.com/YogiLiu/podmaker"
                                       target="_blank">
                                        Podmaker
                                    </a>.
                                    Podcast apps can use the URL in the address bar.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="footer-copyright">
                        <div class="container">
                            <xsl:if test="channel/itunes:owner/itunes:email">
                                <a class="grey-text text-lighten-4">
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="concat('mailto:', channel/itunes:owner/itunes:email)"/>
                                    </xsl:attribute>
                                    Contact Site Owner
                                </a>
                            </xsl:if>
                            <span class="grey-text text-lighten-4 right">
                                Developed by
                                <a class="grey-text text-lighten-4" href="https://github.com/YogiLiu" target="_blank">
                                    YogiLiu
                                </a>
                            </span>
                        </div>
                    </div>
                </footer>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"/>
                <script src="https://cdn.jsdelivr.net/gh/YogiLiu/podmaker/asset/script.js"/>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
