import argparse
import os
import glob
from omegaconf import OmegaConf


action_help = """Action, can be:
- init ; initiliazes the repo according to the venus structure
- ds ; to create a new dataset
- dp ; to create a new dataprep
- xg ; to create a new xperiment group
- xp ; to create a new xperiment
"""

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "venus manager")
	
	parser.add_argument("--action", "-a", default = None, help = action_help)
	parser.add_argument("--tags", "-t", default = None, help = "list of space separated tags for the new artifact")
	parser.add_argument("--datasetid", "-dsi", default = None, help = "id of the dataset to create the dataprep in")
	parser.add_argument("--xpgroupid", "-xgi", default = None, help = "is of the xperiment group to create the xperiment in")

	args = parser.parse_args()
	action = args.action
	

	## Initializing the repo
	if action == "init":

		# creating the .venus folder (empty for now)	
		os.makedirs('.venus/')
		
		# creating the datasets folder
		os.makedirs("datasets/")
		# it will contain a datasets.yaml file which will store the last-dataset-id and the tags of the created datasets
		cfg = OmegaConf.create({
			"last-dataset-id" : 0,
			"datasets-tags" : {}
		})
		OmegaConf.save(cfg, "datasets/datasets.yaml")

		
		# creating the xperiments folder
		os.makedirs("xperiments/")
		# it will contain an xperiments.yaml file which will store the last-xpgroup-id and the tags of the created xpgroups
		cfg = OmegaConf.create({
			"last-xpgroup-id" : 0,
			"xpgroups-tags" : {}
		})
		OmegaConf.save(cfg, "xperiments/xpgroups.yaml")


	## Creating a new dataset
	elif action == "ds":

		# creating the id for the new dataset
		cfg = OmegaConf.load("datasets/datasets.yaml")
		new_dataset_id = cfg["last-dataset-id"] = cfg["last-dataset-id"] + 1
		cfg["datasets-tags"][f"dataset-{new_dataset_id}"] = args.tags
		OmegaConf.save(cfg, "datasets/datasets.yaml")

		# creating the base folder boilerplate
		DIR = f"datasets/dataset-{new_dataset_id}/"
		os.makedirs(DIR)
		with open(DIR+".readme.md", "w") as f:
			f.write("# DESCRIPTION\n\n")
			f.write("# OBTENTION\n\n")
			f.write("# META-DATA\n\n")
			f.write("# DATA-LOCATION\n\n")
		
		# creating the data subfolder with the .gitignore and .gitkeep files
		os.makedirs(DIR+"data")
		with open(DIR+"data/.gitignore", "w") as f:
			f.write("*\n!.gitkeep")
		with open(DIR+"data/.gitkeep", "w") as _:
			pass
		
		# creating the datapreps subfolder with the .gitignore, .gitkeep and datapreps.yaml files
		os.makedirs(DIR+"datapreps")
		with open(DIR+"datapreps/.gitignore", "w") as f:
			f.write("*\n!.gitkeep")
		with open(DIR+"datapreps/.gitkeep", "w") as _:
			pass
		cfg = OmegaConf.create({
			"last-dataprep-id": 0,
			"datapreps-tags": {}
		})
		OmegaConf.save(cfg, DIR+"datapreps/datapreps.yaml")


	## Creating a new dataprep within some dataset
	elif action == "dp":

		# getting the datasetid passed as cli argument 
		dsi = int(args.datasetid)

		# creating the new_dataprepr_id and its entry in the local datapreps.yaml file
		cfg = OmegaConf.load(f"datasets/dataset-{dsi}/datapreps/datapreps.yaml")
		new_dataprep_id =  cfg["last-dataprep-id"] = cfg["last-dataprep-id"] + 1
		cfg["datapreps-tags"][f"dataprep-{new_dataprep_id}"] =  args.tags
		OmegaConf.save(cfg, f"datasets/dataset-{dsi}/datapreps/datapreps.yaml")

		# creating the base folder boilerplate
		DIR = f"datasets/dataset-{dsi}/datapreps/dataprep-{new_dataprep_id}/"
		
		os.makedirs(DIR)
		
		with open(DIR+".readme.md", "w") as f:
			f.write("# DESCRIPTION\n\n")
			f.write("# OBTENTION\n\n")
			f.write("# META-DATA\n\n")
			f.write("# DATA-LOCATION\n\n")
		
		os.makedirs(DIR+"data")
		
		with open(DIR+"data/.gitignore", "w") as f:
			f.write("*\n!.gitkeep")
		with open(DIR+"data/.gitkeep", "w") as f:
			pass
	

	## Creating a new xpgroup
	elif action == "xg":

		# creating the id for the new dataset
		cfg = OmegaConf.load("xperiments/xpgroups.yaml")
		new_id = cfg["last-xpgroup-id"] = cfg["last-xpgroup-id"] + 1
		cfg["xpgroups-tags"][f"xpgroup-{new_id}"] = args.tags
		OmegaConf.save(cfg, "xperiments/xpgroups.yaml")

		# creating the base folder boilerplate
		DIR = f"xperiments/xpgroup-{new_id}/"
		os.makedirs(DIR)

		cfg = OmegaConf.create({
			"last-xp-id": 0,
			"xps-tags": {}
		})
		OmegaConf.save(cfg, DIR+"xps.yaml")
	
	
	## Crearting a new xp
	elif action == "xp":

		# loading the xpgroup_tags
		xgi = int(args.xpgroupid)
		xpgroup_tags = OmegaConf.load("xperiments/xpgroups.yaml")["xpgroups-tags"][f"xpgroup-{xgi}"]

		# creating the new_xp_id and creating the xps-tags entry for the new xp 
		cfg = OmegaConf.load(f"xperiments/xpgroup-{xgi}/xps.yaml")
		new_xp_id = cfg["last-xp-id"] = cfg["last-xp-id"] + 1
		cfg["xps-tags"][f"xp-{new_xp_id}"] = xp_tags = args.tags

		# creating the xp-<id> folder boilerplate
		DIR = f"xperiments/xpgroup-{xgi}/xp-{new_xp_id}/"
		os.makedirs(DIR)
		with open(DIR+".readme.md", "w") as f:
			f.write("# DESCRIPTION\n\n")
			f.write("# OBTENTION\n\n")
			f.write("# META-DATA\n\n")
			f.write("# MODELS-LOCATION\n\n")
		os.makedirs(DIR+"train")
		os.makedirs(DIR+"evals")
		cfg = OmegaConf.create({
			"neptune-id" : f"XPG-{new_xp_id}-XG-{xgi}",
			"xpgroup-tags" : xpgroup_tags,
			"xp-tags" : xp_tags
		})
		OmegaConf.save(cfg, DIR+"xp.yaml")

		
	## Error in the --action cli argument
	else:
		print("ERROR: a valid action (ds, dp, xg, xp) must be supplied")
		exit(-1)