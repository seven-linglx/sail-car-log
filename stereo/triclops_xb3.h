#include <iostream>
#include <triclops.h>
#include <assert.h>
#include <math.h>
#include "bumblebee_xb3.h"
#include "lodepng.h"

#pragma once


void flycap2triclops(const Image& one, const Image& two, TriclopsInput* merged) {
  // NEVER TESTED/DEBUGED BECAREFUL!!!!  
  Image mono_one, mono_two;
  one.Convert( PIXEL_FORMAT_MONO8, &mono_one );
  two.Convert( PIXEL_FORMAT_MONO8, &mono_two );

  if (mono_one.GetCols() != mono_two.GetCols() or mono_one.GetRows() != mono_two.GetRows() or
      mono_one.GetDataSize() != mono_two.GetDataSize()) {
    printf("Error: Image sizes must match");
    exit(-1);
  }

  // free previous type
  // if (merged->u.rgb.red) delete merged->u.rgb.red;
  // if (merged->u.rgb.green) delete merged->u.rgb.green;
  // if (merged->u.rgb.blue) delete merged->u.rgb.blue;
  unsigned int dataSize = mono_one.GetDataSize();
  
  // create type
  merged->inputType 	= TriInp_RGB;
  merged->nrows		= mono_one.GetRows();
  merged->ncols		= mono_one.GetCols();
  merged->rowinc	= mono_one.GetCols();
  merged->u.rgb.red   	= new unsigned char[dataSize];
  merged->u.rgb.green 	= new unsigned char[dataSize];
  merged->u.rgb.blue  	= merged->u.rgb.green;

  // copy data over
  std::copy(mono_one.GetData(), mono_one.GetData()+mono_one.GetDataSize(), (unsigned char*)merged->u.rgb.red);
  std::copy(mono_two.GetData(), mono_two.GetData()+mono_two.GetDataSize(), (unsigned char*)merged->u.rgb.green);  
}



void rgb2rgbu(const std::vector<unsigned char>& rgb, unsigned char** rgbu) {
  // This allocates the data!
  assert((rgb.size() % 3) == 0);
  if (*rgbu) delete *rgbu;
  *rgbu = new unsigned char[(rgb.size()/3)*4];
  int pixel = 0;
  for (int i = 0; i < (rgb.size()/3)*4; i++) {
    if (i%4 < 3) (*rgbu)[i] = rgb[pixel++];
  }
}

void delaceRGB(const std::vector<unsigned char>& rgb, unsigned char** red, unsigned char** green, unsigned char** blue) {
  // This allocates the data!
  assert((rgb.size() % 3) == 0);
  int npixels = rgb.size()/3;

  if (*red) delete *red;
  if (*green) delete *green;
  if (*blue) delete *blue;
  
  *red = new unsigned char[npixels];
  *green = new unsigned char[npixels];
  *blue = new unsigned char[npixels];

  for (int i = 0; i < rgb.size(); i++) {
    if ((i % 3) == 0)
      (*red)[i/3] = rgb[i];
    else if (((i+1)%3) == 0)
      (*green)[i/3] = rgb[i];      
    else if (((i+2)%3) == 0)
      (*blue)[i/3] = rgb[i];
  }
}

double sRGB_to_linear(double x) {
  if (x < 0.04045) return x/12.92;
  return pow((x+0.055)/1.055,2.4);
}

double linear_to_sRGB(double y) {
  if (y <= 0.0031308) return 12.92 * y;
  return 1.055 * pow(y, 1/2.4) - 0.055;
}

unsigned char grayPixel(unsigned char R, unsigned char G, unsigned char B) {
  double R_linear = sRGB_to_linear(R/255.0);
  double G_linear = sRGB_to_linear(G/255.0);
  double B_linear = sRGB_to_linear(B/255.0);
  double gray_linear = 0.299 * R_linear + 0.587 * G_linear + 0.114 * B_linear;
  return round(linear_to_sRGB(gray_linear) * 255);
}

void rgb2gray(const std::vector<unsigned char>& rgb, unsigned char** gray) {
  assert((rgb.size() % 3) == 0);
  if (*gray) delete *gray;
  *gray = new unsigned char[rgb.size()/3];
  for (int i = 0; i < rgb.size(); i+=3 ){
    (*gray)[i/3] = grayPixel(rgb[i], rgb[i+1], rgb[i+2]);
  }
}

void pngReadToTriclopsInput( std::string filename,
			     TriclopsInput* input ) {

  std::vector<unsigned  char> image;
  unsigned width, height;
  lodepng::decode(image, width, height, filename, LCT_RGB);

  input->inputType = TriInp_RGB_32BIT_PACKED;
  input->nrows     = height;
  input->ncols     = width;
  input->rowinc    = 4 * width;
  rgb2rgbu(image, (unsigned char**)&input->u.rgb32BitPacked.data);
}

void pngReadToTriclopsInputRGB( std::string filename,
				TriclopsInput* input) {

  std::vector<unsigned  char> image;
  unsigned width, height;
  lodepng::decode(image, width, height, filename, LCT_RGB);

  input->inputType = TriInp_RGB;
  input->nrows     = height;
  input->ncols     = width;
  input->rowinc    = width;
  delaceRGB(image, (unsigned char**) &input->u.rgb.red,
	    (unsigned char**) &input->u.rgb.green, (unsigned char **) &input->u.rgb.blue);
}


void pngReadToStereoTriclopsInputRGB( const std::string& leftFilename,
				      const std::string& rightFilename,
				      TriclopsInput* input) {
  std::vector<unsigned  char> leftImage;
  unsigned leftWidth, leftHeight;
  lodepng::decode(leftImage, leftWidth, leftHeight, leftFilename, LCT_RGB);

  std::vector<unsigned  char> rightImage;
  unsigned rightWidth, rightHeight;
  lodepng::decode(rightImage, rightWidth, rightHeight, rightFilename, LCT_RGB);
  
  input->inputType = TriInp_RGB;
  input->nrows     = leftHeight;
  input->ncols     = leftWidth;
  input->rowinc    = leftWidth;
  rgb2gray(leftImage, (unsigned char**) &input->u.rgb.red);
  rgb2gray(rightImage, (unsigned char**) &input->u.rgb.green);
  input->u.rgb.blue = input->u.rgb.green;
}

void pngReadToStereoTriclopsInputRGB( const std::string& leftFilename,
				      const std::string& centerFilename,
				      const std::string& rightFilename,
				      TriclopsInput* input) {
  
  pngReadToStereoTriclopsInputRGB(leftFilename, centerFilename, input);
  std::vector<unsigned  char> rightImage;
  unsigned rightWidth, rightHeight;
  lodepng::decode(rightImage, rightWidth, rightHeight, rightFilename, LCT_RGB);
  input->u.rgb.green=NULL;
  rgb2gray(rightImage, (unsigned char**) &input->u.rgb.green);
}


void nullTriclopsInput( TriclopsInput* input ) {
  input->u.rgb.red = NULL;
  input->u.rgb.green = NULL;
  input->u.rgb.blue = NULL;

  input->u.rgb32BitPacked.data=NULL;
}
