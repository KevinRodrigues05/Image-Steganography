from django.shortcuts import render
from .forms import UploadForm, usernameform
from .functions import *

import os
import shutil

import click
from PIL import Image
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

class Steganography(object):

    @staticmethod
    def __int_to_bin(rgb):
        """Convert an integer tuple to a binary (string) tuple.

        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        """Convert a binary (string) tuple to an integer tuple.

        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        """Merge two RGB tuples.

        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple
        (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        """Merge two images. The second one will be merged into the first one.

        :param img1: First image
        :param img2: Second image
        :return: A new merged image.
        """

        # Check the images dimensions
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = Steganography.__int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = Steganography.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img):
        """Unmerge an image.

        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple used to store the image original size
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit
                rgb = (r[4:] + '0000',
                       g[4:] + '0000',
                       b[4:] + '0000')

                # Convert it to an integer tuple
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

                # If this is a 'valid' position, store it
                # as the last valid position
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # Crop the image based on the 'valid' pixels
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image

def merge(img1, img2, output):
    merged_image = Steganography.merge(Image.open(img1), Image.open(img2))
    merged_image.save(output)

def unmerge(img, output):
    unmerged_image = Steganography.unmerge(Image.open(img))
    unmerged_image.save(output)

###################################################################################################


def finalUnmerge(request):
    in_url = "isfinal/static/output.png"
    out_url = "isfinal/static/output2.png"

    unmerge(in_url,out_url)

    return render(request,'result.html')

@login_required(login_url='/accounts/login/')
def home(request):
    if request.method == 'POST':  
        uploadfile = UploadForm(request.POST, request.FILES)
        if uploadfile.is_valid():  
            filename1 = handle_uploaded_file(request.FILES['Cover_image'])
            filename2 = handle_uploaded_file(request.FILES['Image_to_be_merged']) 
        print(filename1)
        print(filename2)

        img_url1 = "isfinal/static/"+filename1
        img_url2 = "isfinal/static/"+filename2
        out_url = "isfinal/static/output.png"

        merge(img_url1,img_url2,out_url)

        
        return render(request,"unmerge.html",{'output':out_url})
    else:

        student = UploadForm()  
        return render(request,"home.html",{'form':student}) 


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            dir_name = "media/"
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            if not os.path.exists(dir_name+username):
                os.mkdir(dir_name+username)

            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})




@login_required(login_url='/accounts/login/')
def sendimage(request):
    if request.method == "POST":

        form = usernameform(request.POST)
        if form.is_valid():
            
            username = form.cleaned_data['Send_to']
            print(username)
            input_url = "isfinal/static/output.png"
            output_url = "media/"+username+"/newImage.png"

            # os.rename(input_url, output_url)
            shutil.move(input_url, output_url)
            # os.replace(input_url, output_url)



        student = UploadForm() 
        return render(request, 'home.html', {'form':student})


    
    sendTo = usernameform()
    return render(request, 'sendto.html',{'form': sendTo})


@login_required(login_url='/accounts/login/')
def inbox(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username


    if request.method == "POST":

        in_url = "media/"+username+"/newImage.png"
        out_url = "isfinal/static/output2.png"

        unmerge(in_url,out_url)

        return render(request,'result.html')



    img_url = "/media/"+username+"/newImage.png"
    return render(request, 'inbox.html', {'img_url': img_url})