## Data Set Establishment Details

### Summary

The dataset contains **53 uncleaned columns** and a variable number of rows, ranging from **25,784 to 180,547 rows** depending on the CSV.

The dataset was pulled from [Virginia Court Data](https://virginiacourtdata.org/). Virginia Court Data is an independent project that scrapes and bulk-releases Virginia Circuit and General District Court case information, available as compressed CSV downloads for free [1]. The open data is **not affiliated with the Commonwealth of Virginia or Virginia's Court System**. The records themselves are created by Virginia's Court System, so they do not have copyright protection.

This dataset provides case-level information, including charges, case types, and dispositions, at scale across the state. The data used in this project covers **criminal cases from Virginia Circuit Courts**, with records ranging from as early as **2000 through 2025**.

The most recent update to the data, released **April 4, 2025**, noted incomplete Circuit Court data for the localities of **Alexandria and Fairfax** [1].

We downloaded the CSV spreadsheets directly from the Virginia Court Data website and converted them to Google Sheets, which are stored in our shared Google Drive folder. There is **one spreadsheet for each year from 2020–2024**, and **three spreadsheets for 2025**, because the 2025 data had to be split into multiple files for easier use.

### Provenance

The data collection and consolidation conducted by the Virginia Court Data website is an independent, private effort created and run as a hobby [1]. The owner(s) recognized that Virginia's court data was not easily accessible in bulk and consolidated the data to make it easier to access and analyze.

Before 2018, Virginia had no law requiring the bulk release of court data. Ben Schoenfeld built a scraper that pulled case information directly from the state's public court-lookup systems, including Circuit and General District Court case searches, and republished the information as downloadable CSV files so that journalists, researchers, and civic technologists would not each have to scrape the data themselves [1].

In 2018, Virginia's **HB 780** took effect, requiring clerks of court to make nonconfidential court records available in bulk. The state itself now also publishes some of this data through official channels, but VirginiaCourtData.org has continued to operate, aggregate, and clean the records. For example, the site removed approximately **100,000 duplicate cases** discovered in April 2019 [1]. It remains a convenient source for bulk downloads of Virginia court data.

Because the underlying records originate from courthouse case-management systems rather than a single centralized, audited source, and because the scraping and reconciliation process is maintained by an independent operator, there is some risk of transcription or merge errors inherited from the original court systems. We treat this as an inherent limitation of the source rather than something we can fully verify ourselves.

### Licensing

There is **no license required to access the data**. The underlying court records are created by Virginia's court system and are government work products. According to the site's terms, they carry no copyright protection and *"may be reused and reproduced freely, without seeking any form of permission from anybody."*

Un-anonymized versions of the same files are available upon request, but only to journalists, nonprofits, academic researchers, or government bodies who register for an account. We are using the **freely available anonymized files**, so this restriction does not apply to our use of the data [1].

### Data Dictionary

The Circuit Court criminal files contain **53 columns**. The fields most relevant to our project are summarized below. Full field-level documentation, maintained by the site owner, is available in the [Virginia Court Data Fields post](https://virginiacourtdata.medium.com/virginia-court-data-fields-e224a9a41e15).

| **Field** | **Type** | **Description** |
|---|---|---|
| `fips` | categorical code | FIPS code of the Circuit Court where the case was filed. Five-digit code: the first two digits represent the state (`51` for Virginia), and the last three digits correspond to the county. |
| `Filed` | date | Date the case was filed. |
| `Commencedby` | categorical | How the case entered Circuit Court (e.g., *Indictment*, *Direct Indictment*, *Reinstatement*, *General District Court Appeal*, *Fail To Appear*). |
| `Locality` | text | Documented as the filing locality, but in practice this field is populated almost entirely with the prosecuting party name (`COMMONWEALTH OF VA`) rather than a city or county. |
| `Sex` | categorical | Defendant's recorded sex: *Female* or *Male*. |
| `Race` | categorical | Recorded race category: *American Indian*, *Asian Or Pacific Islander*, *Black*, *Hispanic*, *White Caucasian*, or *Unknown*. |
| `Address` | text | City and ZIP code where the defendant lives. |
| `Charge` | free text | The criminal charge as entered by the clerk. |
| `CodeSection` | text | Virginia Code (or local ordinance) section allegedly violated. |
| `ChargeType` | categorical | Type of charge: *Felony*, *Misdemeanor*, *Infraction*, *Civil*, or *Other*. |
| `Class` | categorical | Charge severity class (*1*–*6*, where lower numbers represent more severe classes; *U* = unclassified, such as many drug or larceny offenses; *O* = other). |
| `OffenseDate` / `ArrestDate` / `DispositionDate` | date | Key case-timeline dates. These dates are used to compute the arrest-to-disposition gap examined in this project. |
| `DispositionCode` | categorical | Final case outcome, such as *Guilty*, *Not Guilty/Acquitted*, or *Dismissed*. This is our modeling target. Approximately **20% of rows have no disposition recorded**, likely because the case was still open at the time of the scrape. |
| `ConcludedBy` | categorical | Mechanism through which the case was concluded (e.g., *Guilty Plea*, *Trial*). |
| `person_id` | hashed ID | Anonymized identifier that allows the same defendant to be linked across charges and cases without exposing their name. |

### Reference

[1] Virginia Court Data. *Virginia Court Data*. [https://virginiacourtdata.org/](https://virginiacourtdata.org/)