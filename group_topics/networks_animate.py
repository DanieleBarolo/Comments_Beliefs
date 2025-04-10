import imageio
import glob
import os

# Path to the folder containing your PNG files
png_dir = 'group_topics/fig/temporal/20250409_CT_DS70B_002'

# Get a sorted list of PNG files (adjust sorting as needed)
png_files = sorted(glob.glob(os.path.join(png_dir, '*.png')))

# Create a list of images
images = [imageio.imread(file) for file in png_files]

# Save as GIF animation
output_gif = 'network_animation.gif'
imageio.mimsave(output_gif, images, duration=1.0)  # duration is seconds per frame
