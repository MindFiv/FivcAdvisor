def create_tools_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .patches import create_tools_patch

    create_tools_patch()  # apply patches

    from .retrievers import ToolsRetriever

    from crewai_tools import (
        # AIMindTool,
        # ApifyActorsTool,
        # ArxivPaperTool,
        # BraveSearchTool,
        # BrightDataWebUnlockerTool,
        # BrightDataSearchTool,
        # BrightDataDatasetTool,
        # BrowserbaseLoadTool,
        # CodeDocsSearchTool,
        # CodeInterpreterTool,
        # ComposioTool,
        # CouchbaseFTSVectorSearchTool,
        # CrewaiEnterpriseTools,
        # CSVSearchTool,
        # DallETool,
        # DatabricksQueryTool,
        DirectoryReadTool,
        DirectorySearchTool,
        # DOCXSearchTool,
        # EXASearchTool,
        # FileCompressorTool,
        FileReadTool,
        FileWriterTool,
        # FirecrawlCrawlWebsiteTool,
        # FirecrawlScrapeWebsiteTool,
        # FirecrawlSearchTool,
        # GithubSearchTool,
        # HyperbrowserLoadTool,
        # JSONSearchTool,
        # LinkupSearchTool,
        # LlamaIndexTool,
        # MDXSearchTool,
        # MongoDBVectorSearchConfig,
        # MongoDBVectorSearchTool,
        # MultiOnTool,
        # MySQLSearchTool,
        # NL2SQLTool,
        # OxylabsAmazonProductScraperTool,
        # OxylabsAmazonSearchScraperTool,
        # OxylabsGoogleSearchScraperTool,
        # OxylabsUniversalScraperTool,
        # PatronusEvalTool,
        # PatronusLocalEvaluatorTool,
        # PatronusPredefinedCriteriaEvalTool,
        # PDFSearchTool,
        # PGSearchTool,
        # QdrantVectorSearchTool,
        # RagTool,
        # ScrapeElementFromWebsiteTool,
        # ScrapegraphScrapeTool,
        # ScrapegraphScrapeToolSchema,
        ScrapeWebsiteTool,
        # ScrapflyScrapeWebsiteTool,
        # SeleniumScrapingTool,
        # SerpApiGoogleSearchTool,
        # SerpApiGoogleShoppingTool,
        # SerperDevTool,
        # SerperScrapeWebsiteTool,
        # SerplyJobSearchTool,
        # SerplyNewsSearchTool,
        # SerplyScholarSearchTool,
        # SerplyWebpageToMarkdownTool,
        # SerplyWebSearchTool,
        # SingleStoreSearchTool,
        # SnowflakeConfig,
        # SnowflakeSearchTool,
        # SpiderTool,
        # StagehandTool,
        # TavilyExtractorTool,
        # TavilySearchTool,
        # TXTSearchTool,
        # VisionTool,
        # WeaviateVectorSearchTool,
        WebsiteSearchTool,
        # XMLSearchTool,
        # YoutubeChannelSearchTool,
        # YoutubeVideoSearchTool,
        # ZapierActionTools,
    )

    retriever = ToolsRetriever(*args, **kwargs)

    # add a fow default tools
    # retriever.add(retriever.to_tool())
    retriever.add(DirectoryReadTool())
    retriever.add(DirectorySearchTool())
    retriever.add(FileReadTool())
    retriever.add(FileWriterTool())
    # retriever.add(RagTool())
    # retriever.add(SeleniumScrapingTool)
    retriever.add(ScrapeWebsiteTool())
    retriever.add(WebsiteSearchTool())

    return retriever
