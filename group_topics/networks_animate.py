import imageio
import glob
import os

# Path to the folder containing your PNG files
run_id = '20250409_CT_DS70B_002'
basedir = f'fig/temporal/{run_id}'
folders = os.listdir(basedir)

# Create overall directory for pngs
outdir = os.path.join('fig', 'gif', run_id)
if not os.path.exists(outdir): 
    os.makedirs(outdir)

# Loop over each 
for f in folders: 
    png_dir = os.path.join(basedir, f)
    
    # Get a sorted list of PNG files (adjust sorting as needed)
    png_files = sorted(
        glob.glob(os.path.join(png_dir, '*.png')),
        key=lambda x: x.split('start_')[1]  # assuming format "start_date_end_date.png"
    )

    # Create a list of images
    images = [imageio.imread(file) for file in png_files]

    # Save as GIF animation
    output_gif = os.path.join(outdir, f'{f}.gif')
    imageio.mimsave(output_gif, images, fps=5)  # duration is seconds per frame
