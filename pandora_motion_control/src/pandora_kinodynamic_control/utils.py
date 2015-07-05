import math
import numpy
from tf import transformations

def calculate_expected_trajectory(pose, twist, duration, time_granularity):
    """ @brief: Calculates expected trajectory

        Trajectory is a curve with resolution defined by time_granularity
        according to the twist movement command and the duration which
        the command is to be followed.
        Every expected_trajectory must be a arc of a circle with discrete points

    @param pose: vehicle's initial pose at the time of movement command
    @type pose: tuple of doubles (x, y, yaw)
    @param twist: vehicle's movement command (linear & angular vels)
    @type twist: Twist
    @param duration: how much time will the twist be followed
    @type duration: double
    @param time_granularity: resolution of a discrete curve in respect
    to the time. Must be >1 !
    @type time_granularity: double
    @return: list of tuples (x, y, yaw), the expected trajectory

    """

    # Input Data
    linear_vel = twist.linear.x
    angular_vel = twist.angular.z
    robot_x = pose[0]
    robot_y = pose[1]
    robot_yaw = pose[2]

    # Case 1: Linear Movement (angular velocity  = 0)
    if angular_vel == 0:
        # Distance to travel
        distance = linear_vel*duration
        # Step size
        step_size = distance/(time_granularity-1)

        # Pick Points
        points = []
        points_yaw = []
        for i in range(0,time_granularity):
            # Calculate (x,y)
            x = i*step_size
            y = 0
            points.append((x,y))
            points_yaw.append(0)

        # Insert points list in an numpy matrix for tranformations
        points = numpy.matrix(points)
        points = numpy.transpose(points)
        points_yaw = numpy.array(points_yaw)


    # Case 2: Linear + Angular Movement (works also on Linear = 0)
    else:
        # Movement metrics
        r = abs(linear_vel/angular_vel)
        arc_angle = abs(angular_vel)*duration

        # Point Counter
        angle_step = arc_angle/(time_granularity-1)

        if linear_vel<0:
            angle_step = angle_step*(-1)

        # Pick Points:
        points = []
        points_yaw = []
        for i in range(0,time_granularity):
            # Calculate (x,y) based on polar coordinates
            ang = angle_step*i
            x = r * math.sin(ang)
            y = -r* math.cos(ang)

            # Add new point to lists
            points.append((x,y))
            points_yaw.append(ang)

        # Insert points list in an numpy matrix for tranformations
        points = numpy.matrix(points)
        points = numpy.transpose(points)
        points_yaw = numpy.array(points_yaw)

        # 1) Transform first point to (0,0)
        points = points + [[0],[r]]

        # 2) If angular velocity is negative , then , reverse over x axis
        if angular_vel<0:
            points = numpy.matrix([[1,0],[0,-1]])*points
            points_yaw = points_yaw * (-1)


    # --------------------- Transformations ---------------------
    # Rotate points around (0,0)
    [points , points_yaw] = rotate_trajectory(robot_yaw,points,points_yaw)

    # 4) Transform to robot_origin
    points = points + [[robot_x],[robot_y]]

    # 5) Output Form
    points = points.tolist()
    points_x = points[0]
    points_y = points[1]

    points = []
    for i in range(len(points_x)):
        points.append((points_x[i],points_y[i],points_yaw[i]))

    return points

def find_distance(pose_a, pose_b):
    """ @brief: finds distance between two poses in terms of x, y and yaw

    @param pose_a: first pose
    @type pose_a: tuple of doubles (x, y, yaw)
    @param pose_b: second pose
    @type pose_b: tuple of doubles (x, y, yaw)
    @return: double, euclidean distance of (x, y, yaw)

    """

    x_diff = pose_a[0] - pose_b[0]
    y_diff = pose_a[1] - pose_b[1]
    yaw_diff = pose_a[0] - pose_b[2]

    distance = math.sqrt(x_diff**2 + y_diff**2 + yaw_diff**2)
    return distance


def rotate_trajectory(angle,trajectory_points,trajectory_yaw):
    """ @brief: rotates a given trajectory around (0,0) , angle rads.

    @param angle: angle of rotation. (in rads)
    @type angle: double
    @param trajectory_points: points of trajectory to be rotated
    @type trajectory_points: numpy.matrix
    @param trajectory_yaw: rotation of points in trajectory
    @type trajectory_yaw: numpy.array
    @return: list [new_trajectory_points , new_trajectory_yaw]

    """

    # Rotation Matrix
    rotation_matrix = numpy.matrix([[numpy.cos(angle),-numpy.sin(angle)],
                                   [numpy.sin(angle),numpy.cos(angle)]])

    # Multiply points with rotation matrix
    for i in range(trajectory_points[0,:].size):
        trajectory_points[:,i] = rotation_matrix*trajectory_points[:,i]

    trajectory_yaw = trajectory_yaw + angle

    return [trajectory_points,trajectory_yaw]

def discretize_value(x,states):
    """ @brief: Calculates discretized value of a given normallized number.

    @param input: a normallized number (belongs to [-1,1])
    @type input: double
    @param states: number of states
    @type states: integer
    @note: maybe change float states to integers
                    BEWARE : CANCEROUS AREA !!!!
    @note : there is a possibility that little differences in python floating
    system resolve to different states in ActionValueTable()
    @return : an integer number in [0,states-1]
    """
    step_size = 2.0/(states-1)

    # Transformation from [-1,1] to [0,2]
    x = x + 1
    result =  x / step_size

    # Split a number into the integer and decimal
    (decimal_part,int_part) = math.modf(result)

    if decimal_part >=0.5:
        int_part+=1

    return int_part


def hausdorff_distance(A,B):
    """ @brief: Calculates the Hausdorff Distance between 2 sets A and B.

    @param A: set A
    @type A: List of tuples . (in this specific application it is (x,y,yaw))
    @param B: set B
    @type B: List of tuples . (in this specific application it is (x,y,yaw))
    """

    assert(len(A)>0)
    assert(len(B)>0)
    min_distances = []
    for a in A:
        point_distances = []
        for b in B:
            point_distances.append(find_distance(a,b))
        min_distances.append(min(point_distances))

    return max(min_distances)

def state_mapper(a,states):
    """ @brief: Maps a set of integers , representing the state given as a tuple
    substates to an integer representing the total state.Each input combination
    must result in a different integer.

    @param a: Input as substates.
    @type a: tuple of integers
    @param states: List containing total states count of each substate
    @type states: List of integers

    @return: The total state as an integer.
    @note : Logic for achieving so is the following :
        STATES = [N0,N1,N2,...,NK]
          A    = (a0,a1,a2,...,ak)  ,  ai e [0,N0-1]

         Total_state = a0*1 + a1* N0 + a2* N0*N1 + ... + ak *(N0*N1*...*N(K-1))
    """
    # Construct Coefficients vector:
    coefficient = [1]
    for i in range(1,len(a)):
        coefficient.append(coefficient[i-1]*states[i-1])

    total_state = 0

    for i in range(len(a)):
        total_state += a[i]*coefficient[i]

    return total_state
