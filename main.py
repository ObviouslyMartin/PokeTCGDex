if __name__ == '__main__':
    from deck_manager_app import DeckManagerApp
    import logging

    ''' define database path '''
    database = "no_dupes.db"
    # database = "test_db.db"

    '''establish logging service'''
    filename = 'base.log' # TODO:  Append to time / date named log file
    level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=level, filename=filename) 
    logger.info("Starting Application")
    
    ''' run app '''
    dma = DeckManagerApp(database)
    dma.mainloop()
    
    logging.info("Application closed")