# Importing the required libraries
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils import *
from fuzzywuzzy import fuzz

MONTHS = 18

# Defining the Property class with all the attributes
class Property:
    def __init__(self, fips_list, docType_list, FIPS, PropertyID, APN, TaxAccountNumber, SitusFullStreetAddress, SitusCity,
                 SitusState, SitusZIP5, LotSizeSqFt, Owner1LastName, Owner1FirstName, Owner1MiddleName,
                 Owner2LastName, Owner2FirstName, Owner2MiddleName, OwnerNAME1FULL, OwnerNAME2FULL,
                 MailingFullStreetAddress, MailingUnitNbr, MailingCity, MailingState, MailingZIP5,
                 SumLivingAreaSqFt, YearBuilt, EffectiveYearBuilt, CurrentSaleTransactionId, CurrentSaleRecordingDate,
                 CurrentSaleContractDate, CurrentSaleDocumentType, CurrentSalesPrice, CurrentSalesPriceCode,
                 CurrentSaleBuyer1FullName, CurrentSaleBuyer2FullName, CurrentSaleSeller1FullName,
                 CurrentSaleSeller2FullName, PrevSaleTransactionId, PrevSaleRecordingDate, PrevSaleContractDate,
                 PrevSaleDocumentType, PrevSalesPrice, PrevSalesPriceCode, PrevSaleBuyer1FullName,
                 PrevSaleBuyer2FullName, PrevSaleSeller1FullName, PrevSaleSeller2FullName, CurrentAVMValue,
                 vConfidenceScore, RecordingDate_Deed, SaleDate_Deed, DocumentType_Deed, DocumentType_Processed_Deed,
                 SaleAmt_Deed, saleDate_Processed_Deed, Owner_Type, Use_Type, saleDate, totalValue, buildDate, LTV, Absentee):
        self.FIPS = FIPS
        self.PropertyID = PropertyID
        self.APN = APN
        self.TaxAccountNumber = TaxAccountNumber
        self.SitusFullStreetAddress = SitusFullStreetAddress
        self.SitusCity = SitusCity
        self.SitusState = SitusState
        self.SitusZIP5 = SitusZIP5
        self.LotSizeSqFt = LotSizeSqFt
        self.Owner1LastName = Owner1LastName
        self.Owner1FirstName = Owner1FirstName
        self.Owner1MiddleName = Owner1MiddleName
        self.Owner2LastName = Owner2LastName
        self.Owner2FirstName = Owner2FirstName
        self.Owner2MiddleName = Owner2MiddleName
        self.OwnerNAME1FULL = OwnerNAME1FULL
        self.OwnerNAME2FULL = OwnerNAME2FULL
        self.MailingFullStreetAddress = MailingFullStreetAddress
        self.MailingUnitNbr = MailingUnitNbr
        self.MailingCity = MailingCity
        self.MailingState = MailingState
        self.MailingZIP5 = MailingZIP5
        self.SumLivingAreaSqFt = SumLivingAreaSqFt
        self.YearBuilt = YearBuilt
        self.EffectiveYearBuilt = EffectiveYearBuilt
        self.CurrentSaleTransactionId = CurrentSaleTransactionId
        self.CurrentSaleRecordingDate = CurrentSaleRecordingDate
        self.CurrentSaleContractDate = CurrentSaleContractDate
        self.CurrentSaleDocumentType = CurrentSaleDocumentType
        self.CurrentSalesPrice = CurrentSalesPrice
        self.CurrentSalesPriceCode = CurrentSalesPriceCode
        self.CurrentSaleBuyer1FullName = CurrentSaleBuyer1FullName
        self.CurrentSaleBuyer2FullName = CurrentSaleBuyer2FullName
        self.CurrentSaleSeller1FullName = CurrentSaleSeller1FullName
        self.CurrentSaleSeller2FullName = CurrentSaleSeller2FullName
        self.PrevSaleTransactionId = PrevSaleTransactionId
        self.PrevSaleRecordingDate = PrevSaleRecordingDate
        self.PrevSaleContractDate = PrevSaleContractDate
        self.PrevSaleDocumentType = PrevSaleDocumentType
        # For PrevSalesPrice
        try:
            self.PrevSalesPrice = int(PrevSalesPrice)
        except ValueError:
            self.PrevSalesPrice = 0  # or some other default value
        # For PrevSalesPriceCode
        try:
            self.PrevSalesPriceCode = int(PrevSalesPriceCode)
        except ValueError:
            self.PrevSalesPriceCode = None  # or some other default value
        self.PrevSaleBuyer1FullName = PrevSaleBuyer1FullName
        self.PrevSaleBuyer2FullName = PrevSaleBuyer2FullName
        self.PrevSaleSeller1FullName = PrevSaleSeller1FullName
        self.PrevSaleSeller2FullName = PrevSaleSeller2FullName
        self.CurrentAVMValue = CurrentAVMValue
        self.vConfidenceScore = vConfidenceScore
        self.RecordingDate_Deed = RecordingDate_Deed
        self.SaleDate_Deed = SaleDate_Deed
        self.DocumentType_Deed = DocumentType_Deed
        self.DocumentType_Processed_Deed = DocumentType_Processed_Deed
        self.SaleAmt_Deed = SaleAmt_Deed
        self.saleDate_Processed_Deed = saleDate_Processed_Deed
        self.Owner_Type = Owner_Type
        self.Use_Type = Use_Type
        self.saleDate = saleDate
        try:
            self.totalValue = int(totalValue)
        except ValueError:
            self.totalValue = 0
        self.buildDate = buildDate
        self.LTV = LTV
        self.Absentee = Absentee
        self.fips_list = fips_list
        self.docType_list = docType_list
        self.criteria_failures = {
            'base': [],
            'case_1': [],
            'case_2': [],
            'case_3': []
        }
        self.n_County()
        self.n_TotalValue()
        self.n_LivingAreaSqFt()
        self.n_LotSizeSqFt()
        self.n_YearsSinceBuilt()
        self.n_MonthsOwnership()
        self.n_CurrentSaleDate()
        self.n_CurrentSaleValid()
        self.n_CurrentSalesPriceValue()
        self.n_MonthsSinceCurrentSale()
        self.n_PrevSaleDate()
        self.n_PrevSaleValid()
        self.n_PrevSalesPriceValue()
        self.n_DiffSalesPrice()
        self.n_MonthsSincePrevSale()
        self.n_PrevDaysOwnership()
        self.n_DSPtV()
        self.n_CurrentSaleSellerROI()
        self.n_Discounted()
        self.case_1 = self.Case_1()
        self.case_2 = self.Case_2()
        self.case_3 = self.Case_3()



    def __str__(self):
        table = ""
        for attr, value in self.__dict__.items():
            table += f"{attr}: {value}\n"
        return table

    def n_County(self):
        # Convert input to string for consistent comparison
        fips_code = str(self.FIPS)
        
        # Search for the FIPS code in the fips_list
        for fips in self.fips_list:
            if str(fips.fips_code) == fips_code:
                self.n_county = fips.county_name
                return self.n_county
        return None  # Return None if FIPS code not found

    def n_TotalValue(self):
        if self.CurrentAVMValue == "" and self.totalValue == "":
            self.n_totalValue = 0
            print(1, self.n_totalValue)
            return self.n_totalValue
        try:
            self.n_totalValue = int(self.totalValue)
            return self.n_totalValue
        except:
            try:
                self.n_totalValue = float(self.CurrentAVMValue)
                print(3, self.n_totalValue)
                return self.n_totalValue
            except:
                try:
                    self.n_totalValue = float(self.totalValue)
                    print(4, self.n_totalValue)
                    return self.n_totalValue
                except:
                    self.n_totalValue = 0
                    print(5, self.n_totalValue)
                    return self.n_totalValue
    
    def n_LivingAreaSqFt(self):
        self.n_livingAreaSqFt = self.SumLivingAreaSqFt
        return self.n_livingAreaSqFt
    
    def n_LotSizeSqFt(self):
        self.n_lotSizeSqFt = self.LotSizeSqFt
        return self.n_lotSizeSqFt
    
    # USAR BUILT DATE (ARREGLAR)
    def n_YearsSinceBuilt(self):
        if str(self.YearBuilt) == 'nan' or str(self.YearBuilt) == "":
            self.n_yearsSinceBuilt = ""
            return self.n_yearsSinceBuilt
        try:       
            year_built = int(str(self.YearBuilt)[:4])
            start_date = datetime(year=1900, month=1, day=1)
            end_date = datetime.today()
            delta = relativedelta(end_date, start_date.replace(year=year_built))
            years_since_built = delta.years + delta.months / 12.0 + delta.days / 365.25
            self.n_yearsSinceBuilt = round(years_since_built,2)
            return self.n_yearsSinceBuilt
        except:
            self.n_yearsSinceBuilt = ""
            return self.n_yearsSinceBuilt
      
    def n_MonthsOwnership(self):
        if self.saleDate == "Unknown" or self.saleDate == "":
            self.n_monthsOwnership = ""
            return self.n_monthsOwnership
        try:
            sale_date = datetime.strptime(self.saleDate, "%d-%m-%y")
        except ValueError:
            self.n_monthsOwnership = ""
            return self.n_monthsOwnership

        end_date = datetime.today()
        delta = (end_date - sale_date).days
        if delta == 0:
            self.n_monthsOwnership = 0
            return 0
        year_frac = delta / 365.25  # Average number of days per year, accounting for leap years
        months_ownership = year_frac * 12
        self.n_monthsOwnership = round(months_ownership, 2)
        return self.n_monthsOwnership
    
    def n_CurrentSaleDate(self):
        try:
            recording_date_value = float(self.CurrentSaleRecordingDate)
        except (ValueError, TypeError):
            recording_date_value = 0.0
        
        try:
            contract_date_value = float(self.CurrentSaleContractDate)
        except (ValueError, TypeError):
            contract_date_value = 0.0
        self.n_currentSaleDate = (max(recording_date_value, contract_date_value))
        
        try:
            self.n_currentSaleDate = int(self.n_currentSaleDate)
            return self.n_currentSaleDate
        except (ValueError):
            return self.n_currentSaleDate
    
    def n_CurrentSaleValid(self):
        docType = self.CurrentSaleDocumentType
        for doc in self.docType_list:
            if doc.docType_code == str(docType.replace(".0","")):
                self.n_currentSaleValid = doc.sale
                return self.n_currentSaleValid
        self.n_currentSaleValid = ""
        return self.n_currentSaleValid
    
    def n_CurrentSalesPriceValue(self):
        self.n_currentSalesPriceValue = int(float(self.CurrentSalesPrice))
        return self.n_currentSalesPriceValue
    
    def n_MonthsSinceCurrentSale(self):
        try:
            self.n_currentSaleDate = str(self.n_currentSaleDate)  # Convert to string if it's not
            year = int(self.n_currentSaleDate[:4])
            month = int(self.n_currentSaleDate[4:6])
            day = int(self.n_currentSaleDate[6:])
            
            sale_valid_date = datetime(year=year, month=month, day=day)
            end_date = datetime.today()

            delta = relativedelta(end_date, sale_valid_date)
            months_since_current_sale = delta.years * 12 + delta.months + delta.days / 30.44  # Approximate days to months

            self.n_monthsSinceCurrentSale = round(months_since_current_sale, 3)
            return self.n_monthsSinceCurrentSale

        except (ValueError, TypeError, IndexError) as e:
            self.n_monthsSinceCurrentSale = ""
            return self.n_monthsSinceCurrentSale
    
    def n_PrevSaleDate(self):
        try:
            recording_date_value = float(self.PrevSaleRecordingDate)
        except (ValueError, TypeError):
            recording_date_value = 0.0
        
        try:
            contract_date_value = float(self.PrevSaleContractDate)
        except (ValueError, TypeError):
            contract_date_value = 0.0
        self.n_prevSaleDate = max(recording_date_value, contract_date_value)
        try:
            self.n_prevSaleDate = int(self.n_prevSaleDate)
            return self.n_prevSaleDate
        except (ValueError, TypeError):
            return self.n_prevSaleDate
    
    def n_PrevSaleValid(self):
        try:
            docType = self.PrevSaleDocumentType
            for doc in self.docType_list:
                if doc.docType_code == str(docType.replace(".0","")):
                    self.n_prevSaleValid = doc.sale
                    return self.n_prevSaleValid
            self.n_prevSaleValid = ""
            return self.n_prevSaleValid
        except:
            return ""

    def n_PrevSalesPriceValue(self):
        try:
            self.n_prevSalesPriceValue = int(self.PrevSalesPrice)
            return self.n_prevSalesPriceValue
        except:
            return 0
    
    def n_MonthsSincePrevSale(self):        
        try:
        # Convert float to string and pad with zeros if necessary
            n_prevSaleDate_str = str(int(self.n_prevSaleDate)).zfill(8)
            
            year = int(n_prevSaleDate_str[:4])
            month = int(n_prevSaleDate_str[4:6])
            day = int(n_prevSaleDate_str[6:8])
            
            n_prev_sale_date = datetime(year=year, month=month, day=day)
            end_date = datetime.today()
            
            delta = relativedelta(end_date, n_prev_sale_date)
            months_since_n_prev_sale = delta.years * 12 + delta.months + delta.days / 30.44
            self.n_monthsSincePrevSale = round(months_since_n_prev_sale,2)
            return int(self.n_monthsSincePrevSale)
        except (ValueError, TypeError, IndexError):
            self.n_monthsSincePrevSale = ""
            return self.n_monthsSincePrevSale

    def n_PrevDaysOwnership(self):
        try:
            # Convert float to string and pad with zeros for n_prevSaleDate
            n_prevSaleDate_str = str(int(self.n_prevSaleDate)).zfill(8)
            year_prev = int(n_prevSaleDate_str[:4])
            month_prev = int(n_prevSaleDate_str[4:6])
            day_prev = int(n_prevSaleDate_str[6:8])
            prev_sale_date = datetime(year=year_prev, month=month_prev, day=day_prev)
            # Convert float to string and pad with zeros for n_currentSaleDate
            n_currentSaleDate_str = str(int(self.n_currentSaleDate)).zfill(8)
            year_current = int(n_currentSaleDate_str[:4])
            month_current = int(n_currentSaleDate_str[4:6])
            day_current = int(n_currentSaleDate_str[6:8])
            current_sale_date = datetime(year=year_current, month=month_current, day=day_current)
            # Calculate the days between the two dates
            delta = current_sale_date - prev_sale_date
            self.n_prevDaysOwnership = delta.days
            return self.n_prevDaysOwnership
        except (ValueError, TypeError, IndexError):
            self.n_prevDaysOwnership = ""
            return self.n_prevDaysOwnership

    def n_DiffSalesPrice(self):
        try: 
            current_price = float(self.n_currentSalesPriceValue)
            prev_price = float(self.n_prevSalesPriceValue)
            if current_price == 0 or prev_price == 0:
                self.n_diffSalesPrice = ""
                return self.n_diffSalesPrice
        
            self.n_diffSalesPrice = int(current_price - prev_price)
            return self.n_diffSalesPrice
        except ValueError:
            self.n_diffSalesPrice = ""
            return self.n_diffSalesPrice
            
    def n_DSPtV(self):
        if self.n_currentSaleValid == "Y" and self.n_prevSaleValid == "Y":
            try:
                self.n_dSPtV = round(float(self.n_diffSalesPrice) / float(self.totalValue),2)
                return self.n_dSPtV 
            except (ValueError, ZeroDivisionError):
                self.n_dSPtV = ""
                return self.n_dSPtV 
        self.n_dSPtV = ""
        return self.n_dSPtV 
    
    def n_CurrentSaleSellerROI(self):
        if self.n_currentSaleValid == "Y" and self.n_prevSaleValid == "Y":
            try:
                if float(self.n_currentSalesPriceValue) == 0 or float(self.n_prevSalesPriceValue) == 0:
                    self.n_currentSaleSellerROI = ""
                    return self.n_currentSaleSellerROI
                self.n_currentSaleSellerROI = round(float(self.n_currentSalesPriceValue) / float(self.n_prevSalesPriceValue),3)
                return self.n_currentSaleSellerROI
            except (ValueError, ZeroDivisionError):
                self.n_currentSaleSellerROI = ""
                return self.n_currentSaleSellerROI
        self.n_currentSaleSellerROI = ""
        return self.n_currentSaleSellerROI
    
    def n_Discounted(self):
        if self.n_currentSaleValid == "Y" and self.n_prevSaleValid == "Y":
            try:
                current_price = float(self.n_currentSalesPriceValue)
                prev_price = float(self.n_prevSalesPriceValue)
            except ValueError:
                self.n_discounted = ""
                return self.n_discounted

            if current_price == 0 or prev_price == 0:
                self.n_discounted = ""
                return self.n_discounted
            else:
                self.n_discounted = round(prev_price / current_price,3)
                return self.n_discounted
        else:
            self.n_discounted = ""
            return self.n_discounted

    def are_names_similar(self):
        similarity_score = fuzz.ratio(self.CurrentSaleSeller1FullName.upper().strip(), self.PrevSaleBuyer1FullName.upper().strip())
        return similarity_score > 85  # You can tune the threshold as needed

    def convert_to_int(self, value, default=-1):
        """Intenta convertir un valor a int, devuelve un valor predeterminado si falla."""
        # Si el valor es una cadena, intentar convertirlo tras comprobar si es numérico
        if isinstance(value, str):
            try:
                # strip() elimina espacios en blanco y isdigit() verifica si todos los caracteres son dígitos
                # Pero primero verificamos si es una cadena que representa un flotante
                if value.strip().replace('.', '', 1).isdigit() or value.strip().lstrip('-').replace('.', '', 1).isdigit():
                    return int(float(value))
                else:
                    return default
            except ValueError:
                return default
        # Si el valor ya es un número (int o float), convertir directamente a int
        elif isinstance(value, (int, float)):
            return int(value)
        else:
            return default


    # MISSING: Mailing address remains unchanged between owners
    def Base_criteria(self):
        names_are_similar = self.are_names_similar()
        price_condition = int(self.n_prevSalesPriceValue) >= 10000
        failures = []

        if not names_are_similar:
            failures.append("names_are_not_similar")
        if not price_condition:
            failures.append("price_below_10000")

        if failures:
            self.criteria_failures['base'].extend(failures)
            return False
        else:
            return True
            
    # CASE 1: Double Close
    def Case_1(self):
        failures = []
        if not self.Base_criteria():
            failures.append("base_criteria_failed")
        
        # Convertir valores relevantes a enteros
        n_monthsSincePrevSale = self.convert_to_int(self.n_monthsSincePrevSale)
        n_monthsSinceCurrentSale = self.convert_to_int(self.n_monthsSinceCurrentSale)
        n_yearsSinceBuilt = self.convert_to_int(self.n_yearsSinceBuilt)
        n_diffSalesPrice = self.convert_to_int(self.n_diffSalesPrice)
        n_prevDaysOwnership = self.convert_to_int(self.n_prevDaysOwnership)
        n_currentSalesPriceValue = self.convert_to_int(self.n_currentSalesPriceValue)
        totalValue = self.convert_to_int(self.totalValue)

        # Actualizar las condiciones para usar los valores convertidos
        criteria_checks = [
            ("prev_sale_conditions_not_met", lambda: n_monthsSincePrevSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("current_sale_conditions_not_met", lambda: n_monthsSinceCurrentSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("years_since_built_not_specified_or_less_or_equal_3", lambda: n_yearsSinceBuilt <= 3),
            ("diff_in_sales_price_not_specified_or_out_of_bounds", lambda: n_diffSalesPrice <= 10000 or n_diffSalesPrice > n_currentSalesPriceValue * 0.4),
            ("prev_days_ownership_out_of_bounds_0_3", lambda: not (0 <= n_prevDaysOwnership <= 3)),
            ("current_sales_price_too_low", lambda: n_currentSalesPriceValue <= 0.10 * totalValue or n_currentSalesPriceValue <= 20000)
        ]

        for failure_msg, check in criteria_checks:
            if check():
                failures.append(failure_msg)

        if failures:
            self.criteria_failures['case_1'].extend(failures)
            return False
        else:
            return True

    # CASE 2: Wholetail
    def Case_2(self):
        failures = []
        if not self.Base_criteria():
            failures.append("base_criteria_failed")
        
        # Convertir valores relevantes a enteros
        n_monthsSincePrevSale = self.convert_to_int(self.n_monthsSincePrevSale)
        n_monthsSinceCurrentSale = self.convert_to_int(self.n_monthsSinceCurrentSale)
        n_yearsSinceBuilt = self.convert_to_int(self.n_yearsSinceBuilt)
        n_diffSalesPrice = self.convert_to_int(self.n_diffSalesPrice)
        n_prevDaysOwnership = self.convert_to_int(self.n_prevDaysOwnership)
        n_currentSalesPriceValue = self.convert_to_int(self.n_currentSalesPriceValue)
        totalValue = self.convert_to_int(self.totalValue)

        # Actualizar las condiciones para usar los valores convertidos
        criteria_checks = [
            ("prev_sale_conditions_not_met", lambda: n_monthsSincePrevSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("current_sale_conditions_not_met", lambda: n_monthsSinceCurrentSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("years_since_built_not_specified_or_less_or_equal_3", lambda: n_yearsSinceBuilt <= 3),
            ("diff_in_sales_price_not_specified_or_out_of_bounds", lambda: n_diffSalesPrice < 10000 or n_diffSalesPrice > n_currentSalesPriceValue * 0.5),
            ("prev_days_ownership_out_of_bounds_4_60", lambda: not (4 <= n_prevDaysOwnership <= 60)),
            ("current_sales_price_too_low", lambda: n_currentSalesPriceValue <= 0.10 * totalValue or n_currentSalesPriceValue <= 20000)
        ]

        for failure_msg, check in criteria_checks:
            if check():
                failures.append(failure_msg)

        if failures:
            self.criteria_failures['case_2'].extend(failures)
            return False
        else:
            return True
    
    # CASE 3: Fix & FLip
    def Case_3(self):
        failures = []
        if not self.Base_criteria():
            failures.append("base_criteria_failed")

        # Convertir valores relevantes a enteros
        n_monthsSincePrevSale = self.convert_to_int(self.n_monthsSincePrevSale)
        n_monthsSinceCurrentSale = self.convert_to_int(self.n_monthsSinceCurrentSale)
        n_yearsSinceBuilt = self.convert_to_int(self.n_yearsSinceBuilt)
        n_diffSalesPrice = self.convert_to_int(self.n_diffSalesPrice)
        n_prevDaysOwnership = self.convert_to_int(self.n_prevDaysOwnership)
        n_currentSalesPriceValue = self.convert_to_int(self.n_currentSalesPriceValue)
        totalValue = self.convert_to_int(self.totalValue)

        # Actualizar las condiciones para usar los valores convertidos
        criteria_checks = [
            ("prev_sale_conditions_not_met", lambda: n_monthsSincePrevSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("current_sale_conditions_not_met", lambda: n_monthsSinceCurrentSale > MONTHS or self.n_prevSaleValid != "Y"),
            ("years_since_built_not_specified_or_less_or_equal_5", lambda: n_yearsSinceBuilt <= 5),
            ("diff_in_sales_price_not_specified_or_out_of_bounds", lambda: n_diffSalesPrice <= 10000 or n_diffSalesPrice > n_currentSalesPriceValue * 0.6),
            ("prev_days_ownership_out_of_bounds_61_365", lambda: not (61 <= n_prevDaysOwnership <= 365*1.5)),
            ("current_sales_price_too_low", lambda: n_currentSalesPriceValue <= 0.10 * totalValue or n_currentSalesPriceValue <= 20000)
        ]

        for failure_msg, check in criteria_checks:
            if check():
                failures.append(failure_msg)

        if failures:
            self.criteria_failures['case_3'].extend(failures)
            return False
        else:
            return True