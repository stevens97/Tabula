def clean_table(table, year):
    
    '''
    The clean_table function cleans a given table.
    The table is expected to have the format of a "Ten-year review Salient features* table"
    (found in Investec Annual reports).
    
    **The following assumptions are made**:
    - The first cell of the table should contain the phrase "For the year ended".
    This way, the function knows how to reorganise the cell.
    
    params:
    table [pandas.core.frame.DataFrame]: The table that needs to be cleaned.
    
    returns:
    table [pandas.core.frame.DataFrame]: The cleaned table.
    '''
    
    # Calculate number of rows and columns in the table
    n_row = len(table.iloc[:,0]) # number of rows
    n_col = len(table.iloc[0,:]) # number of columns
    
    '''
    The table is expected to start with the phrase "For the year ended", therefore the first cell 
    should contain this phrase.
    
    If however, the table was misread to not start here (and contains some empty rows or columns)
    these empty rows and columns should be removed and the table should be shifted upwards and 
    leftwards to start at the right place.
    '''
    feature_r = 0
    feature_c = 0
    # Scan through the table to find the phrase "For the year ended"
    for r in range(n_row): # Search through each row.
        for c in range(n_col): # Search through each column.
            # Find the row and column containing this phrase.
            if type(table.iloc[r,c]) == str:
                if 'For the year ended' in table.iloc[r,c]:
                    feature_r = r
                    feature_c = c
                    table.iloc[r,c]
                    break;
    # Shift table up the correct amount.
    if feature_r > 0:
        table = table.shift(axis = 0, periods = -feature_r)
    # Shift table left the correct amount.
    if feature_c > 0:
        table = table.shift(axis = 1, periods = -feature_c)
    
    # Delete empty rows and columns after the table has been shifted.
    if feature_r > 0 and feature_c > 0:
        table = table.iloc[:-feature_r,:-feature_c]
    elif feature_r > 0 and not feature_c > 0:
        table = table.iloc[:-feature_r,:]
    elif not feature_r > 0 and feature_c > 0:
        table = table.iloc[:,:-feature_c]
    
    # Set the headers of the table to be the text stored within the 1st row of the table.
    # (No longer use indeces, since we now know the correct header information)
    table.columns = table.iloc[0,:]
    table = table.iloc[1:,:]
    table = table.reset_index(drop = True)
    n_row = len(table.iloc[:,0])
    n_col = len(table.iloc[0,:])
    
    
    '''
    In some cases, due to a cell containing a very long sentence, a row within the table was split into two rows.
    
    To solve this, we need to combine these rows back together, making sure we don't combine any rows that 
    shouldn't be combined.
    
    Rows that shouldn't be combined contain the phrases:
    - Income statement and selected returns
    - Balance sheet
    - table financial features and key statistics
    
    These rows are skipped.
    '''
    
    # Set the rows that can be skipped.
    titles = ['Income statement and selected returns',
             'Balance sheet',
             'table financial features and key statistics']
    
    # Initialise variable; to contain all row numbers that should later be dropped.
    tbd = []
    
    # Search through every row. When a row was split over two lines, the first row will be filled with NaN values.
    # (This is how tabula would read and split the rows).
    # To fix this, we simply add the text from the two row names together. (By adding it into the 2nd row).
    for r in range(0, n_row-1):
        if ( pd.isna(np.array(table.iloc[r,1:])).all() ) and (table.iloc[r,0] not in titles) and (table.iloc[r+1,0] not in titles):
            tbd = np.append(tbd, r) # Add first row (filled with NaN values) to list of rows that should be dropped.
            # Add the text from the two row names together. (Add to 2nd row).
            table.iloc[r+1,0] = table.iloc[r,0] + ' ' + table.iloc[r+1,0] 
    table.drop(tbd, axis=0, inplace=True) # Drop empty rows filled with NaN values.
    table = table.reset_index(drop = True) # Reset index
    
    '''
    Lastly, we need to make sure that the data within the table is the correct type and doesn't contain any
    characters that shouldn't be there. (Such as strange non-ASCII characters).
    '''
    
    for i in range(1,table.shape[0]):
        for j in range(1,table.shape[1]):
            if type(table.iloc[i,j]) is str:
                # Reformat numbers, ex: 300 000 --> 300000
                table.iloc[i,j] = table.iloc[i,j].replace(' ', '')
                # Remove strange non-ASCII characters from table.
                table.iloc[i,j] = re.sub('[^0-9.,%x^]', '', table.iloc[i,j])
            
    
    while table.iloc[0,0] != 'Income statement and selected returns':
        table.columns = table.iloc[0,:]
        table = table.shift(axis = 0, periods = -1)
        table.drop(table.tail(1).index,inplace=True)
        table = table.reset_index(drop = True) # Reset index
    
    # Remove strange non-ASCII characters from row names and column names.
    try:
        table.iloc[:,0] = table.iloc[:,0].str.encode('ascii', 'ignore').str.decode('ascii')
        table.columns = table.columns.str.encode('ascii', 'ignore').str.decode('ascii')
    except:
        pass
    
    columns = np.array(table.columns, dtype = str)
    for i in range(len(columns)):
        columns[i] = columns[i].replace('*','')
        
        if '% change' in columns[i]:
            columns[i] = '{} vs {}'.format(year, year-1)
    columns[0] = 'For the year ended 31 March'
    table.columns = columns
    
    table = table[table.columns.drop(list(table.filter(regex='nan')))]

    
        
    return table