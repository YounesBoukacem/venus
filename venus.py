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
		os.makedirs(".venus/")
		cfg = OmegaConf.create({
			"neptune-name" : None,
			"neptune-token" : None
		})
		OmegaConf.save(cfg, ".venus/neptune.db")
		
		# creating the datasets folder
		os.makedirs("datasets/")
		# it will contain a datasets.yaml file which will store the last-dataset-id and the tags of the created datasets
		cfg = OmegaConf.create({
			"last-dataset-id" : 0,
			"datasets" : {}
		})
		OmegaConf.save(cfg, "datasets/datasets.db")

		
		# creating the xperiments folder
		os.makedirs("xperiments/")
		# it will contain an xperiments.yaml file which will store the last-xpgroup-id and the tags of the created xpgroups
		cfg = OmegaConf.create({
			"last-xpgroup-id" : 0,
			"xpgroups" : {}
		})
		OmegaConf.save(cfg, "xperiments/xperiments.db")
	

	# synchronize the xperiments.db and xpgroup-<id>.db tags with xp-<xgi>-<xpi>.conf
	# WARNING: This supposes that all tags modifications are done through the dbs and not directly in the confs, synchronizing will overwrite
	elif action == "sync":
		xperiments_db = OmegaConf.load("xperiments/xperiments.db")
		for xpgroup_id, xpgroup_tags in xperiments_db["xpgroups"].items():
			print(xpgroup_id,":",xpgroup_tags)
			xpgroup_db = OmegaConf.load(f"xperiments/{xpgroup_id}/{xpgroup_id}.db")
			for xp_id, xp_tags in xpgroup_db["xps"].items():
				xp_conf = OmegaConf.load(f"xperiments/{xpgroup_id}/{xp_id}/{xp_id}.conf")
				xp_conf["xpgroup-tags"] = xpgroup_tags
				xp_conf["xp-tags"] = xp_tags
				OmegaConf.save(xp_conf, f"xperiments/{xpgroup_id}/{xp_id}/{xp_id}.conf")
	
	
	## Creating a new dataset
	elif action == "ds":

		# creating the id for the new dataset
		cfg = OmegaConf.load("datasets/datasets.db")
		new_dataset_id = cfg["last-dataset-id"] = cfg["last-dataset-id"] + 1
		cfg["datasets"][f"dataset-{new_dataset_id}"] = args.tags
		OmegaConf.save(cfg, "datasets/datasets.db")

		# creating the base folder boilerplate
		DIR = f"datasets/dataset-{new_dataset_id}/"
		os.makedirs(DIR)
		with open(DIR+"readme.md", "w") as f:
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
		os.makedirs(DIR+f"datapreps-{new_dataset_id}/")
		cfg = OmegaConf.create({
			"last-dataprep-id": 0,
			"datapreps": {}
		})
		OmegaConf.save(cfg, DIR+f"datapreps-{new_dataset_id}/datapreps-{new_dataset_id}.db")


	## Creating a new dataprep within some dataset
	elif action == "dp":

		# getting the datasetid passed as cli argument 
		dsi = int(args.datasetid)

		# creating the new_dataprepr_id and its entry in the local datapreps.yaml file
		cfg = OmegaConf.load(f"datasets/dataset-{dsi}/datapreps-{dsi}/datapreps-{dsi}.db")
		new_dataprep_id =  cfg["last-dataprep-id"] = cfg["last-dataprep-id"] + 1
		cfg["datapreps"][f"dataprep-{dsi}-{new_dataprep_id}"] =  args.tags
		OmegaConf.save(cfg, f"datasets/dataset-{dsi}/datapreps-{dsi}/datapreps-{dsi}.db")

		# creating the base folder boilerplate
		DIR = f"datasets/dataset-{dsi}/datapreps-{dsi}/dataprep-{dsi}-{new_dataprep_id}/"
		
		os.makedirs(DIR)
		
		with open(DIR+"readme.md", "w") as f:
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
		cfg = OmegaConf.load("xperiments/xperiments.db")
		new_xpgroup_id = cfg["last-xpgroup-id"] = cfg["last-xpgroup-id"] + 1
		cfg["xpgroups"][f"xpgroup-{new_xpgroup_id}"] = args.tags
		OmegaConf.save(cfg, "xperiments/xperiments.db")

		# creating the base folder boilerplate
		DIR = f"xperiments/xpgroup-{new_xpgroup_id}/"
		os.makedirs(DIR)

		cfg = OmegaConf.create({
			"last-xp-id": 0,
			"xps": {}
		})
		OmegaConf.save(cfg, DIR+f"xpgroup-{new_xpgroup_id}.db")
	
	
	## Crearting a new xp
	elif action == "xp":

		# loading the xpgroup_tags
		xgi = int(args.xpgroupid)
		xpgroup_tags = OmegaConf.load("xperiments/xperiments.db")["xpgroups"][f"xpgroup-{xgi}"]

		# creating the new_xp_id and creating the xps-tags entry for the new xp 
		cfg = OmegaConf.load(f"xperiments/xpgroup-{xgi}/xpgroup-{xgi}.db")
		new_xp_id = cfg["last-xp-id"] = cfg["last-xp-id"] + 1
		cfg["xps"][f"xp-{xgi}-{new_xp_id}"] = xp_tags = args.tags
		OmegaConf.save(cfg, f"xperiments/xpgroup-{xgi}/xpgroup-{xgi}.db")
		
		# creating the xp-<id> folder boilerplate
		DIR = f"xperiments/xpgroup-{xgi}/xp-{xgi}-{new_xp_id}/"
		os.makedirs(DIR)
		with open(DIR+"readme.md", "w") as f:
			f.write("# DESCRIPTION\n\n")
			f.write("# OBTENTION\n\n")
			f.write("# META-DATA\n\n")
			f.write("# MODELS-LOCATION\n\n")
		os.makedirs(DIR+"train")
		os.makedirs(DIR+"evals")
		cfg = OmegaConf.create({
			"neptune-id" : f"XPG-{xgi}-XP-{new_xp_id}",
			"xpgroup-tags" : xpgroup_tags,
			"xp-tags" : xp_tags
		})
		OmegaConf.save(cfg, DIR+f"xp-{xgi}-{new_xp_id}.conf")


	## Error in the --action cli argument
	else:
		print("ERROR: a valid action (init, ds, dp, xg, xp) must be supplied")
		exit(-1)