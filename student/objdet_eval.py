# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Evaluate performance of object detection
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# general package imports
import numpy as np
import matplotlib
# matplotlib.use('wxagg') # change backend so that figure maximizing works on Mac as well
import matplotlib.pyplot as plt

import torch
from shapely.geometry import Polygon
from operator import itemgetter

# add project directory to python path to enable relative imports
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

# object detection tools and helper functions
import misc.objdet_tools as tools


def calculate_iou(gt_bbox, pred_bbox):
    """
    calculate iou
    args:
    - gt_bbox [array]: 1x4 single gt bbox
    - pred_bbox [array]: 1x4 single pred bbox
    returns:
    - iou [float]: iou between 2 bboxes
    """
    xmin = np.max([gt_bbox[0], pred_bbox[0]])
    ymin = np.max([gt_bbox[1], pred_bbox[1]])
    xmax = np.min([gt_bbox[2], pred_bbox[2]])
    ymax = np.min([gt_bbox[3], pred_bbox[3]])
    print(xmin, ymin, xmax, ymax)
    intersection = max(0, xmax - xmin) * max(0, ymax - ymin)
    gt_area = (gt_bbox[2] - gt_bbox[0]) * (gt_bbox[3] - gt_bbox[1])
    pred_area = (pred_bbox[2] - pred_bbox[0]) * (pred_bbox[3] - pred_bbox[1])

    union = gt_area + pred_area - intersection
    print(intersection, union)
    return intersection / union


# compute various performance measures to assess object detection
def measure_detection_performance(detections, labels, labels_valid, min_iou=0.5):
    # find best detection for each valid label
    true_positives = 0  # no. of correctly detected objects
    center_devs = []
    ious = []
    for label, valid in zip(labels, labels_valid):
        matches_lab_det = []
        if valid:  # exclude all labels from statistics which are not considered valid

            # compute intersection over union (iou) and distance between centers

            ####### ID_S4_EX1 START #######
            #######
            print("student task ID_S4_EX1 ")

            ## step 1 : extract the four corners of the current label bounding-box
            box = label.box
            label_corners = tools.compute_box_corners(box.center_x, box.center_y, box.width, box.length, box.heading)
            print('label_corners', label_corners)
            match_box = None
            ## step 2 : loop over all detected objects
            for detection in detections:
                ## step 3 : extract the four corners of the current detection
                pred_corners = tools.compute_box_corners(detection[1].item(),
                                                         detection[2].item(),
                                                         detection[5].item(),
                                                         detection[6].item(),
                                                         detection[7].item())
                print('pred_corners', pred_corners)
                ## step 4 : computer the center distance between label and detection bounding-box in x, y, and z
                pred_center = np.array([detection[1], detection[2], detection[3]])
                label_center = np.array([box.center_x, box.center_y, box.center_z])
                center_dist = label_center - pred_center
                print('center_dist', center_dist)
                ## step 5 : compute the intersection over union (IOU) between label and detection bounding-box
                iou = calculate_iou([label_corners[1][0], label_corners[1][1],
                                     label_corners[3][0], label_corners[3][1]],
                                    [pred_corners[1][0], pred_corners[1][1],
                                     pred_corners[3][0], pred_corners[3][1]])
                print('iou', iou)
                ## step 6 : if IOU exceeds min_iou threshold, store [iou,dist_x, dist_y, dist_z] in matches_lab_det and increase the TP count
                if iou > min_iou:
                    match_box = [iou, center_dist[0], center_dist[1], center_dist[2]]
                    matches_lab_det.append(match_box)
                    true_positives += 1
            #######
            ####### ID_S4_EX1 END #######

        # find best match and compute metrics
        if matches_lab_det:
            best_match = max(matches_lab_det,
                             key=itemgetter(1))  # retrieve entry with max iou in case of multiple candidates
            ious.append(best_match[0])
            center_devs.append(best_match[1:])

    ####### ID_S4_EX2 START #######
    #######
    print("student task ID_S4_EX2")

    # compute positives and negatives for precision/recall

    ## step 1 : compute the total number of positives present in the scene
    all_positives = len(detections)

    ## step 2 : compute the number of false negatives
    valid_label_cnt = 0
    for each in labels_valid:
        if each:
            valid_label_cnt += 1
    false_negatives = valid_label_cnt - true_positives

    ## step 3 : compute the number of false positives
    false_positives = all_positives - true_positives

    #######
    ####### ID_S4_EX2 END #######

    pos_negs = [all_positives, true_positives, false_negatives, false_positives]
    det_performance = [ious, center_devs, pos_negs]

    return det_performance


# evaluate object detection performance based on all frames
def compute_performance_stats(det_performance_all):
    # extract elements
    ious = []
    center_devs = []
    pos_negs = []
    for item in det_performance_all:
        ious.append(item[0])
        center_devs.append(item[1])
        pos_negs.append(item[2])

    ####### ID_S4_EX3 START #######
    #######
    print('student task ID_S4_EX3')

    ## step 1 : extract the total number of positives, true positives, false negatives and false positives
    pos_negs_arr = np.asarray(pos_negs)
    positives = sum(pos_negs_arr[:, 0])
    true_positives = sum(pos_negs_arr[:, 1])
    false_negatives = sum(pos_negs_arr[:, 2])
    false_positives = sum(pos_negs_arr[:, 3])
    print("TP = " + str(true_positives) + ", FP = " + str(false_positives) + ", FN = " + str(false_negatives))

    ## step 2 : compute precision
    precision = true_positives / (true_positives + false_positives)

    ## step 3 : compute recall
    recall = true_positives / (true_positives + false_negatives)

    #######
    ####### ID_S4_EX3 END #######
    print('precision = ' + str(precision) + ", recall = " + str(recall))

    # serialize intersection-over-union and deviations in x,y,z
    ious_all = [element for tupl in ious for element in tupl]
    devs_x_all = []
    devs_y_all = []
    devs_z_all = []
    for tuple in center_devs:
        for elem in tuple:
            dev_x, dev_y, dev_z = elem
            devs_x_all.append(dev_x)
            devs_y_all.append(dev_y)
            devs_z_all.append(dev_z)

    # compute statistics
    stdev__ious = np.std(ious_all)
    mean__ious = np.mean(ious_all)

    stdev__devx = np.std(devs_x_all)
    mean__devx = np.mean(devs_x_all)

    stdev__devy = np.std(devs_y_all)
    mean__devy = np.mean(devs_y_all)

    stdev__devz = np.std(devs_z_all)
    mean__devz = np.mean(devs_z_all)
    # std_dev_x = np.std(devs_x)

    # plot results
    data = [precision, recall, ious_all, devs_x_all, devs_y_all, devs_z_all]
    titles = ['detection precision', 'detection recall', 'intersection over union', 'position errors in X',
              'position errors in Y', 'position error in Z']
    textboxes = ['', '', '',
                 '\n'.join((r'$\mathrm{mean}=%.4f$' % (np.mean(devs_x_all),),
                            r'$\mathrm{sigma}=%.4f$' % (np.std(devs_x_all),),
                            r'$\mathrm{n}=%.0f$' % (len(devs_x_all),))),
                 '\n'.join((r'$\mathrm{mean}=%.4f$' % (np.mean(devs_y_all),),
                            r'$\mathrm{sigma}=%.4f$' % (np.std(devs_y_all),),
                            r'$\mathrm{n}=%.0f$' % (len(devs_x_all),))),
                 '\n'.join((r'$\mathrm{mean}=%.4f$' % (np.mean(devs_z_all),),
                            r'$\mathrm{sigma}=%.4f$' % (np.std(devs_z_all),),
                            r'$\mathrm{n}=%.0f$' % (len(devs_x_all),)))]

    f, a = plt.subplots(2, 3)
    a = a.ravel()
    num_bins = 20
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    for idx, ax in enumerate(a):
        ax.hist(data[idx], num_bins)
        ax.set_title(titles[idx])
        if textboxes[idx]:
            ax.text(0.05, 0.95, textboxes[idx], transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=props)
    plt.tight_layout()
    plt.show()

