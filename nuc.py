import sys
sys.path.append('fancypipe')
sys.path.append('niitools')
from fancypipe import *
import niitools
import os.path as op
import nibabel
import numpy

class NonUniformityCorrection(FancyTask):
  title = 'Correct individual coronal sections for nonuniform lighting'
  description = 'Use Nick Tustison\'s N4 non-uniformity correction'
  inputs = odict(
    'inp', {'type':assertFile, 'help':'Input image.'},
    'out', {'type':assertOutputFile,'help':'Output image.'},
    'maxiter',{'type':int,'default': 200, 'help':'Maximum number of iterations.'},
    'convthr',{'type':float,'default':0.0001, 'help':'Convergence threshold, ratio of intensity changes between iterations.'},
    'dist',{'type':float,'default':50.0,'help':'Bspline control point spacing in mm.'},
    'shrink',{'type':int,'default':4,'help':'Shrink factor, amount of subsampling of the input image.'}
  )
  
  def main(self,inp,out,maxiter,convthr,dist,shrink):
    # load data
    nii = nibabel.load(inp)
    img = nii.get_data()

    title = 'Apply the N4 bias field correction to each coronal slice'
    q = nii.get_header().get_best_affine()
    outfiles = FancyList()
    for j in range(0,img.shape[1]):
      # create nifti file for individual slice
      FANCYDEBUG(q,q[:,[0,2,1,3]])
      nii = nibabel.Nifti1Image(img[:,j,:],q[:,[0,2,1,3]])
      infile = self.tempfile('section_{}.nii.gz'.format(j))
      nibabel.save(nii,infile)
      outfile = self.tempfile('section_{}_n4.nii.gz'.format(j))
      n4bfc = FancyExec().setCwd('/home/rbakker/Install/ANTs/release/bin').setProg('N4BiasFieldCorrection').setInput(
        **{
          '-i' : infile,
          '-o' : outfile,
          '-c' : '[%s,%s]' % (maxiter,convthr),
          '-b' : '[%s]' % dist,
          '-s' : str(shrink),
          '-v' : '2'
        }
      )
      outfiles.append(n4bfc.requestOutput('-o'))

    outfiles.resolve()
    for (j,outfile) in enumerate(outfiles):
      nii = nibabel.load(outfile)
      img[:,j,:] = nii.get_data()

    nii = nibabel.Nifti1Image(img,q)
    nibabel.save(nii,out)
    return out
#endclass


if __name__ == '__main__':
  NonUniformityCorrection.fromCommandLine().run()
