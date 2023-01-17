def find_table(keyword, p_start, p_end, pdf):
    
    '''
    The find_table function finds the first table in the pdf file containing the specified keyword 
    within its cells, or which has the keyword in its title or heading. 
    
    The table is searched for between the pages p_start and p_end of the given pdf file.
    
    params:
    keyword [str]: Keyword or title that needs to be found.
    p_start [int]: Page number to start looking from.
    p_end [int]: Page number to stop at.
    pdf [str]: File name of the pdf to search through.
    
    returns:
    table [pandas.core.frame.DataFrame]: The table that was found as a dataframe.
    '''
    
    # Set initial conditions
    # ---------------------------------------------------------
    p = p_start # Start searching from page number *p_start*.
    flag = True # While loop condition, Loop till False.
    found = False # Specifies whether a table could be found. Starts off as false.
    
    # Search through PDF
    # ---------------------------------------------------------
    print(colored('Scanning through {}...'.format(pdf), 'blue'))
    
    # Search until the table is found. With each iteration increase the page number.
    # Break when the table is found or when all pages have been scanned through.
    while flag is True:
        # Use tabula to find all tables on page *p* for the pdf file.
        
        # guess = False, such that tabula doesn't guess the proportions of the table.
        # In this case tabula will then read all text & information surrounding the table, 
        # such as titles, headings etc. and include it as part of the tabular data.
        
        # This can be taken advantage of to test whether the specified *keyword* is in the title of the table.
        # pandas_options = {'header': None}. 
        # This is merely a preference. Indeces are prefered to access columns. 
        # (We don't know what the correct header information is yet, the table still needs to be cleaned.)
        
        tables = tabula.read_pdf(pdf, pages = p, guess = False,
                                 pandas_options={'header': None}) # Read page *p*
        print('Checking page {} for a table with the keyword: "{}\"...'.format(p, keyword))
        
        # For each table found by tabula...
        for t in tables:
            # Scan through all of the tabular data...
            for v in t.values:
                # Scan through the information within each cell...
                for w in v.tolist():
                    # If the information within the cell is text-based:
                    if type(w) is str:
                        w = w.lower()
                        # Check whether the keyword is in the cell or not.
                        # If so:
                        if keyword in w:
                            page = p # Set the page number to where the table was found.
                            found = True
                            flag = False # Stop searching.
                            print(colored('Table was found on page {}!\n'.format(p), 'green'))
                            
        # If all pages have been scanned through.
        if p > p_end:
            flag = False # Stop searching.
            print(colored('Table couldn\'t be found on pages {}-{} in {}'.format(p_start, p_end, pdf), 'red'))
            print('Please try again.\n')
        
        # Increment page number. With the next iteration, scan through the next page.
        p = p + 1
    
    # If the table was found. Read the table from the correct page with tabula.
    # guess = True, such that tabula guesses the proportions of the table.
    if found is True:
        
        # Check if table is split over 2 pages when reading
        test1 = tabula.read_pdf(pdf, pages = page, guess = True, stream = True,
                                pandas_options={'header': None})
        test1 = test1[0]
        
        test2 = tabula.read_pdf(pdf, pages = page+1, guess = True, stream = True,
                                pandas_options={'header': None})
        
        test2 = test2[0]
        
        if (len(test1.iloc[0,:]) >= 1) and (len(test2.iloc[0,:]) >= 1):
            
            table = pd.concat([test1, test2])
        else:
            
            table = test1
            
    
    return table