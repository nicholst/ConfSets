import numpy as np 
import os
import time
import matplotlib.pyplot as plt
from generateData import *


# TODO:
# - cleanup

# field - field to thresh
# c - thresh
# d - dimension along which we get bdry
def get_bdry_map(field, c, d): 

    # Get field dimensions
    dim = field.shape

    # Get boolean for where field is greater than c
    exc_set = field>2

    # ----------------------------------------------------------------------
    # Work out shift down and shift up indices
    # ----------------------------------------------------------------------
    # Initialize empty index collections
    up_indices = np.empty(shape=(len(dim)),dtype=object)
    down_indices = np.empty(shape=(len(dim)),dtype=object)


    # Loop through indices and join them in a list
    for i in np.arange(len(dim)):

        # If the d is not the i^th dimension keep all rows
        if d == i:

            # Add all but last to up indices
            up_indices[i] = np.arange(dim[i]-1)

            # Add all but first to down indices
            down_indices[i] = np.arange(1, dim[i])

        # If the d is not the i^th dimension keep all rows
        else:

            # Add full numpy range to both up and down
            up_indices[i] = np.arange(dim[i])
            down_indices[i] = np.arange(dim[i])

    # Padding dimensions to add zeros back on at the end (basically just 
    # same as dim but with the d^th dimension set to 1
    pdim = np.array(dim)
    pdim[d] = 1

    # ----------------------------------------------------------------------
    # Bottom boundary
    # ----------------------------------------------------------------------

    # Boundary without the bottom row (we can't assess downwards violations
    # when there is no data below)
    bdry_wo_bottom = exc_set[np.ix_(*up_indices)]

    # Complement of boundary downwards shifted
    shif_bdry_bottom = np.logical_not(exc_set[np.ix_(*down_indices)])

    # The boundary "below" the excursion set in this dimension
    bottom_bdry = bdry_wo_bottom*shif_bdry_bottom

    # Inner bottom bdry - add back on a bottom row
    bottom_bdry_inner = np.concatenate((bottom_bdry,np.zeros(pdim)),axis=d)

    # Outer bottom bdry - add back on a top row
    bottom_bdry_outer = np.concatenate((np.zeros(pdim),bottom_bdry),axis=d)

    # ----------------------------------------------------------------------
    # Top boundary
    # ----------------------------------------------------------------------

    # Boundary without the top row (we can't assess upwards violations
    # when there is no data above)
    bdry_wo_top = exc_set[np.ix_(*down_indices)]

    # Complement of boundary upwards shifted
    shif_bdry_top = np.logical_not(exc_set[np.ix_(*up_indices)])

    # The boundary "above" the excursion set in this dimension
    top_bdry = bdry_wo_top*shif_bdry_top

    # Inner top bdry - add back on a top row
    top_bdry_inner = np.concatenate((np.zeros(pdim),top_bdry),axis=d)

    # Outer top bdry - add back on a bottom row
    top_bdry_outer = np.concatenate((top_bdry,np.zeros(pdim)),axis=d)

    return(bottom_bdry_inner, bottom_bdry_outer, top_bdry_inner, top_bdry_outer)


def get_bdry_maps(field, c):

    # Shape of field
    shape = np.array(field.shape)

    # Dimension of field
    dim = np.array(field.ndim)

    # Make an empty dictionary to store boundaries
    bdry_maps = dict()

    # Loop through dimensions of field and get the boundary boolean maps.
    for d in np.arange(dim):

        # Dimensions of 1 are assumed to be uninteresting as they are usually 
        # only included for broadcasting purposes.
        if shape[d]>1:

            # Get boundaries
            bottom_inner, bottom_outer, top_inner, top_outer = get_bdry_map(field, c, d)

            # Record d^th boundary
            bdry_maps[d] = dict()

            # Add bottom boundaries
            bdry_maps[d]['bottom'] = dict()

            # Add inner and outer bottom boundaries
            bdry_maps[d]['bottom']['inner'] = bottom_inner
            bdry_maps[d]['bottom']['outer'] = bottom_outer

            # Add top boundaries
            bdry_maps[d]['top'] = dict()

            # Add inner and outer top boundaries
            bdry_maps[d]['top']['inner'] = top_inner
            bdry_maps[d]['top']['outer'] = top_outer

    # Add the non-flat (>1) dimensions as an array for good measure
    bdry_maps['dims'] = np.arange(dim)[shape>1]

    # Save original field shapes
    bdry_maps['shape_orig'] = np.array(field.shape)

    # Save original field dimension
    bdry_maps['dim_orig'] = np.array(field.ndim)

    # Return the bounaries
    return(bdry_maps)

def get_bdry_locs(bdry_maps):

    # Make an empty dictionary to store boundaries
    bdry_locs = dict()

    # Directions we can interpolate in
    directions = ['bottom', 'top']

    # -------------------------------------------------------------------------------------
    # Minimal dimensions (i.e. dimensions we would have if all dimensions of length 1 were
    # removed
    # -------------------------------------------------------------------------------------
    # Read in 0^th dimension to get a boundary image to work with
    dims = bdry_maps['dims']

    # Get the new shape we want to record indices for.
    new_shape = bdry_maps['shape_orig'][dims]

    # -------------------------------------------------------------------------------------
    # Loop through dimensions of field and get the locations of the boundary in the 
    # boundary boolean maps.
    # -------------------------------------------------------------------------------------
    for d in bdry_maps['dims']:

        # Record d^th boundary
        bdry_locs[d] = dict()

        # Loop through all directions getting locations
        for direction in directions:

            # Add bottom boundaries
            bdry_locs[d][direction] = dict()

            # Get inner map and reshape 
            inner = bdry_maps[d][direction]['inner'].reshape(new_shape)

            # Get outer map and reshape 
            outer = bdry_maps[d][direction]['outer'].reshape(new_shape)

            # Get coordinates of non-zero entries
            bdry_locs[d][direction]['inner'] = np.where(inner)
            bdry_locs[d][direction]['outer'] = np.where(outer)

    # Add the non-zero dimensions as an array for good measure
    bdry_locs['dims'] = bdry_maps['dims']

    # Return the bounaries
    return(bdry_locs)


def get_bdry_values(field, bdry_locs):

    # New dictionary to store boundary values
    bdry_vals = dict()

    # Directions we can interpolate in
    directions = ['bottom', 'top']

    # Loop through dimensions of field and get the boundary boolean maps.
    for d in bdry_locs['dims']:

        # Record d^th boundary
        bdry_vals[d] = dict()

        # Loop through all directions getting locations
        for direction in directions:

            # Record d^th boundary
            bdry_vals[d][direction] = dict()

            # Get inner and outer boundary values in this dimension and
            # direction            
            inner_vals = field[...,(*bdry_locs[d][direction]['inner'])]
            outer_vals = field[...,(*bdry_locs[d][direction]['outer'])]

            # Record boundary values
            bdry_vals[d][direction]['inner'] = inner_vals
            bdry_vals[d][direction]['outer'] = outer_vals

    # Add the non-zero dimensions as an array for good measure
    bdry_vals['dims'] = bdry_locs['dims']

    # Return boundary values
    return(bdry_vals)

def get_bdry_weights(bdry_vals,c):

    # New dictionary to store weights for interpolation along boundary
    bdry_weights = dict()

    # Directions we can interpolate in
    directions = ['bottom', 'top']

    # Loop through dimensions of field and get the boundary boolean maps.
    for d in bdry_vals['dims']:

        # Record d^th boundary
        bdry_weights[d] = dict()

        # Loop through all directions getting locations
        for direction in directions:

            # Record d^th boundary
            bdry_weights[d][direction] = dict()

            # Get inner and outer boundary values in this dimension and
            # direction            
            inner_vals = bdry_vals[d][direction]['inner']
            outer_vals = bdry_vals[d][direction]['outer']

            # Temporarily turn off divide by 0 warnings, we'll handle these below
            # (This is over cautious... it only really is a problem for plateua 
            # mu fields)
            with np.errstate(divide='ignore'):
                
                # Work out weights
                bdry_weights[d][direction]['outer']= (inner_vals-c)/(inner_vals-outer_vals)
                bdry_weights[d][direction]['inner']= (c-outer_vals)/(inner_vals-outer_vals)

            # In case we had 2 values which were the same (can happen when looking down
            # on ramp)
            inf_locs = np.isinf(bdry_weights[d][direction]['inner'])

            # Replace infs
            bdry_weights[d][direction]['inner'][inf_locs]=1
            bdry_weights[d][direction]['outer'][inf_locs]=0

    # Add the non-zero dimensions as an array for good measure
    bdry_weights['dims'] = bdry_vals['dims']

    # Return boundary values
    return(bdry_weights)



def get_bdry_vals_interpolated(bdry_vals,bdry_weights,dictform=False):

    # New dictionary to store weights for interpolation along boundary
    bdry_interp = dict()

    # Directions we can interpolate in
    directions = ['bottom', 'top']

    # Boolean to tell if this is the first edge we are looking at.
    first = True

    # Loop through dimensions of field and get the boundary boolean maps.
    for d in bdry_vals['dims']:

        # Record d^th boundary
        bdry_interp[d] = dict()

        # Loop through all directions getting locations
        for direction in directions:

            # Get inner and outer boundary values in this dimension and
            # direction            
            outer_vals = bdry_vals[d][direction]['outer']
            inner_vals = bdry_vals[d][direction]['inner']

            # Work out weights
            outer_weights = bdry_weights[d][direction]['outer']
            inner_weights = bdry_weights[d][direction]['inner']
        
            # Work out interpolated values
            bdry_interp[d][direction] = inner_weights*inner_vals + outer_weights*outer_vals

            # If this is the first edge we've looked at initialise 
            # concatenated interpolated boundary array
            if first:

                # Initialise array
                bdry_interp_concat = bdry_interp[d][direction]

                # We're no longer looking at the first edge
                first = False

            else:

                # Add the boundary values we just worked out
                bdry_interp_concat =  np.concatenate((bdry_interp_concat,bdry_interp[d][direction]),axis=-1)

    # If we have set dictform to true, return the boundry values in dictionary
    # form, i.e. preserving which edge each value came from. (more useful for
    # bug testing)
    if dictform:

        # Add the non-zero dimensions as an array for good measure
        bdry_interp['dims'] = bdry_vals['dims']

        # Return boundary values in dictionary form
        return(bdry_interp)

    # Otherwise just return them all in one big concatenated array (default -
    # more useful in practice)
    else:

        # Return boundary values in concatenated form
        return(bdry_interp_concat)

def testfn():

    data, mu = get_data('rampHoriz2D', np.array([100,100,100]), np.array([0,5,5]))

    muhat = np.mean(data,axis=0).reshape(mu.shape)

    # plt.figure(0)
    # plt.imshow(muhat[0,:,:])

    # plt.figure(1)
    # plt.imshow(muhat[0,:,:]>2)

    # plt.figure(2)
    print('maps')
    t1 = time.time()
    bdry_maps = get_bdry_maps(muhat, 2)
    t2 = time.time()
    print(t2-t1)

    print('locs')
    t1 = time.time()
    bdry_locs = get_bdry_locs(bdry_maps)
    t2 = time.time()
    print(t2-t1)

    print('vals')
    t1 = time.time()
    bdry_vals=get_bdry_values(muhat, bdry_locs)
    t2 = time.time()
    print(t2-t1)

    print('weights')
    t1 = time.time()
    bdry_weights=get_bdry_weights(bdry_vals,2)
    t2 = time.time()
    print(t2-t1)

    t1 = time.time()
    bdry_vals=get_bdry_values(muhat, bdry_locs)
    t2 = time.time()

    print('interp')
    t1 = time.time()
    bdry_interp=get_bdry_vals_interpolated(bdry_vals,bdry_weights)
    t2 = time.time()
    print(t2-t1)

    # print(bdry_maps)

    # bdrys2 = get_bdry_maps(data, 2)

    # print(bdrys2)


    # plt.imshow(bdry_maps[1]['top']['inner'][0,:,:]+bdry_maps[1]['bottom']['inner'][0,:,:]+bdry_maps[2]['top']['inner'][0,:,:]+bdry_maps[2]['bottom']['inner'][0,:,:])
    # plt.figure(3)
    # plt.imshow(bdry_maps[1]['top']['outer'][0,:,:]+bdry_maps[1]['bottom']['outer'][0,:,:]+bdry_maps[2]['top']['outer'][0,:,:]+bdry_maps[2]['bottom']['outer'][0,:,:])

    # plt.show()