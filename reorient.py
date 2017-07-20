import sys
sys.path.append('fancypipe')
sys.path.append('niitools')
from fancypipe import *
import niitools
import os.path as op
import nibabel
import numpy

# preprocessing part of the hippocampus segmentation pipeline

def px2mm(niifile):
  nii = nibabel.load(niifile)
  q = nii.get_affine()
  return numpy.linalg.det(q)


class Reorient(FancyTask):
  title = 'Rearrange data such that +i,+j,+k become (close to) Right,Anterior,Superior'
  inputs = odict(
    'inp', {'type':assertFile, 'help':'Input image.'},
    'out', {'type':assertOutputFile,'help':'Output image.'},
    'reorient', {'type':str, 'default':'+i+j+k', 'help':'Requested flipping and permutation, e.g. \'+i+j+k\''}
  )
  
  def main(self,inp,out,reorient):
    nii = nibabel.load(inp)
    nii = niitools.reorient(nii,reorient)
    nii = nibabel.as_closest_canonical(nii)
    # remove trailing singleton dimension
    hdr = nii.get_header()
    shape = hdr.get_data_shape()
    if shape[-1] == 1:
      img = nii.get_data()
      img = img.squeeze(-1)
      nii = nibabel.nifti1.Nifti1Image(img,hdr.get_best_affine())
    nibabel.nifti1.save(nii, out)
    return out
#endclass

if __name__ == '__main__':
  Reorient.fromCommandLine().run()
