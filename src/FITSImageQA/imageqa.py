"""
something descriptive, perform several checks 

author: wpb-astro
date XYZ
"""

# proper way to load sextractor config
# from config_sextractor import 

class Thing:
    def __init__(self) -> None:
        """
        # initial the header object
        # initial the data object
        # --> c.f. MRF and how it 
        """
        pass
    
    def RENAME_setup_logging(self): # someway to set up logging / keeping track of what flags are triggered
        pass

    def is_corrupt_or_empty(self):
        """check whether the FITS file is corrupt or empty
        """
        pass

class QAHeader(Thing):
    def __init__(self, hdr, expected_fields=None, expected_fields_dtype=None) -> None:
        """
        hdr : can be a filename, or an hdu (result of fits.open), or fitsheader object (hdu[0].header)
        expected_fields : iterable of str
        expected_fields_dtype : iter of key-value pairs
            keys = header names (str)
            values = data types        
        """
        super().__init__()
        self.hdr = hdr
        # (!) TODO: is it bad practice to set new attribute, if not explicitly passed in init?
        self.header_fields = set(self.hdr.keys())
        try:
            self.expected_fields = set(expected_fields)
        except TypeError:
            self.expected_fields = expected_fields
        self.expected_fields_dtype = expected_fields_dtype

    def check_header_fields_present(self, expected_fields=None, 
                                    return_missing_fields=False):
        """
        parameters
        ----------
        expected_fields : iterable of str (optional)
            if passed, use instead of self.expected_fields 
        return_missing_fields : bool (default=False)
            if True, return fields from `expected_fields` that 
            are not present in image header
        
        returns
        -------
        valid : bool
            are the desired fields present in the header?
        missing_fields : iter, optional
            which fields are missing from the header (empty, if valid=True)
        """
        if expected_fields is not None:
            expected_fields = set(expected_fields)
        else:
            expected_fields = self.expected_fields
        # check whether all desired fields are present
        valid = self.header_fields.issuperset( expected_fields )
        if not return_missing_fields:
            return valid
        else:
            missing_fields = expected_fields.difference( self.header_fields )
            return valid, missing_fields
    
    def check_header_fields_dtype(self, expected_fields_dtype=None,
                                  return_incorrect_fields=False,
                                  suppress_unknown=False, verbose=False):
        """
        check that data type of header fields are as expected
        
        Parameters
        ----------
        expected_fields_dtype : iter of key-value pairs
            keys = header names (str)
            values = data types
        return_incorrect_fields : bool
            which fields are of the wrong data type (empty, if valid=True)
        suppress_unknown : bool
            if True, do not break if header datatype cannot be checked 
            (not in reference list)
        verbose : bool
            print warnings if fields cannot be checked, or if fields are wrong data type
        
        Returns
        -------
        valid : bool
            are the header fields of the expected data type?
        """
        pass
        
    

class QAData(Thing):
    def __init__(self, config_sextractor=None) -> None:
        super().__init__()
        if config_sextractor is not None:
            self.set_config_sextractor( config_sextractor )
        else:
            self.config_sextractor = lOADED_SEXTRACTOR_CONFIG
        
    def set_config_sextractor(self, config_sextractor):
        """
        IS THIS THE APPROPRIATE WAY TO SET ATTRIBUTE? CALLED DURING INIT? CALLED LATER, 
            E.G., WHEN RUNNING `run_sextractor` ??
        """
        pass

    def is_focus_good(self): #or, rename as check_focus
        """determine whether a focus run is needed while observing"""
        pass

    def run_sextractor(self, ):
        # should the header be updated???
        pass

    # same checks that are done during dfreduce
    #   this package will be called during dfreduce - see how this is done (what is ingested / returned)
    # see how mrf / dfreduce do their file checks (empty/corrupt)