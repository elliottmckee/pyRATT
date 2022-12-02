'''

I will be coming back to this later to expand this header a good bit


Description:
This will be the main script that the User interacts with. 
They will select which modules to run, point to the desired
rocket/trajectory files, maybe point to a config file 
containing extra information, and this will hand things off to simulate.py


'''

#from materials_standard import SolidMaterial



from materials_database.materials_standard import SolidMaterial






if __name__ == "__main__":


    Wall_Material = SolidMaterial("OTHER EXAMPLE MATERIAL")


    print(Wall_Material.rho)











