""" Module lidar_positioning
    A paket to monitor the position of a moving LiDAR
    based on 2-dimensional point clouds.
    The module uses the Iterative Closest Point (ICP) algorithm
    
    At this point in time it is  experimental software ...
    Source: https://learnopencv.com/iterative-closest-point-icp-explained/
    SLW - February 2026
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
            
        
def transform_pc(pc, angdgr, tx, ty):
    """ Rotates and/or translates a point cloud to a new position:
        pc -> 2D point cloud
        angdgr -> rotation angle (degrees)
        tx, ty -> translation in horizontal and vertical direction
        Returns: transformed point cloud """
    theta = -angdgr * np.pi / 180
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    t = np.array([tx, ty])
    return (pc @ R.T) + t
        
        
def rigid_transform_2d(src, trg):
    """ Calculates a transformation (rotation 'R' + translation 't')
        from a source to a target  point clouds.
        The points in both clouds need to be matched.
        src: Nx2 array of source points
        trg: Nx2 array of target points (corresponding to src)
        returns R (2x2), t (2,)
    """

    # Center both point cloudes
    src_mean = src.mean(axis=0)
    trg_mean = trg.mean(axis=0)
    src_c = src - src_mean
    trg_c = trg - trg_mean
    # 2x2 covariance
    H = src_c.T @ trg_c
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    # Fix reflection
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    # Get resulting transformation matrix
    t = trg_mean - src_mean @ R
    return R, t


def icp_2d(src, trg, angdgr_guess=0.0, tx_guess=0.0, ty_guess=0.0,
           max_iters=50, tol=1e-6, verbose=False):
    """ Estimates a transformation (rotation 'R' + translation 't') based on two 2D point clouds.
        1) Applies a kd_tree to find matching points in both clouds.
        2) Iterates an ICD algorithm to estimate the best trasnformation matrices
        src, trg: numpy arrays, shape(n, 2)
        R_total and t_total can take the initial guess (if available)
        returns Rotation matrix (2x2), translation vector (2,)
    """
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='kd_tree').fit(trg)
    # Initial transformation matrices
    theta = -angdgr_guess * np.pi / 180
    R_total = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]])
    t_total = np.array([tx_guess, ty_guess])
    # Run the loop
    prev_err = np.inf
    for idx in range(max_iters):
        # Transform source with current estimate
        src_transformed = src @ R_total.T + t_total
        # Find nearest neighbors in dst
        distances, indices = nbrs.kneighbors(src_transformed)
        trg_corr = trg[indices[:, 0]]
        # Compute optimal rigid transform for these correspondences
        R_delta, t_delta = rigid_transform_2d(src_transformed, trg_corr)
        # Update global transform
        R_total = R_delta @ R_total
        t_total = t_delta + t_total @ R_delta.T
        # Check stop condition
        mean_err = distances.mean()        
        if abs(prev_err - mean_err) < tol:
            break
        prev_err = mean_err
            
    theta_dgr = -np.arctan2(R_total[1,0], R_total[0,0]) * 180 / np.pi
    tx, ty = t_total[0], t_total[1]
    if verbose:
        print("lidar_positioning - icp_2d")
        print(" - Iterations: " + str(idx))
        print(" - Remaining error: " + str(round(mean_err, 1)))
        print(" - Rotation angle: " + str(round(theta_dgr, 1)) + " degree")
        print(" - Movement x:", round(tx, 1), "  y:", round(ty, 1))
        print()
    return theta_dgr, tx, ty, mean_err, idx

