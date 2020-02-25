# dedupclaims
repository to dedup incoming claims at large healthcare HMO/CMOs


Duplicate logic:
1.	Simstg_create is the primary program to create the simstring and leveldb
2.	It is created usually under base folder(.)  ./output/dup-simstring.db and dupids.db.
3.	When executing, we have to give the installation path and destination path.
4.	Installation file (duplicate_file.csv) will be the entire volume of enterprise claims dump that has everything (originals +duplicates).
5.	Main_mod.py is the main class that holds duplicate logic.
6.	Main_implement.py sends the details from duplicate_file_check.csv to Match method in main_mod.py to check for similar duplicates. 
7.	It outputs information in the following order:

claim | dup_claim_id | member_id | dos_start_dt | dos_end_dt | npi | paid_amt | procedure_code | similarity

8.	Similarity is a measure of duplicates.  It is an exact duplicate if it scores 1.   Anything greater than .6- .7 is considered a duplicate.
9.	Claim id and dup_claim_id are both presented to remediate any claims.
10.	This project speeds up the existing duplicate logic implemented on OLAP databases, which are extremely slow.
