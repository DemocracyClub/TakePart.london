# Voter registration information

This project does a number of things:

1. Provides some scripts work manipulating and storying electoral registers
2. Provides a web interface for exploring ward level aggregated stats for a postcode.
3. Provides some tools for adding those stats to local images, designed for sharing.

## Registers

Importing:

1. Place a register in `data/electoral_rolls/[gss]-[council-name]/`.
* Convert the register to a CSV file (if it isn't one already).  The format can be TSV or CSV, but the file name needs to end with `.csv`:
  * Run the script `data/electoral_rolls/convert_to_csvs.sh` with the folder name as the first argument: `sudo convert_to_csvs.sh E123-trumpton`. Note that `sudo` is required, and `soffice` needs to the on the `PATH`.

  * Alternatively find another way to convert the file to a CSV and save it alongside the register in the `[gss]-[council-name]` folder.

2. In the 'web' folder, run `./manage.py clean_data_files`.  Do clean a single register, you can add `--gss E123` as an argument. This will convert the CSV created in the previous step in to the format needed for the web system. It does the following:

  1. Removes all data we're not interested in, like names and voter numbers.
  2. Converts split address fields in to a single field.
  3. Makes a postcode column from any column that looks like it might be a postcode
  4. Ignores lines that don't look valid (mainly, without a postcode)

3. Import the file in to the database: `./manage.py import_cleaned_data`. You can pass a `--gss` argument to this command, as above.

4. Geocode the data: `./manage.py geocode_addresses`

5. Update the population data: `manage.py import_population_data`


## Images

### Per register:

Once the steps in "Registers" above have been run, you need to add generated images to the new data:

`./manage.py create_images_for_wards`
