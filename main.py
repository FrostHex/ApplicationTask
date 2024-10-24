import cv2
import numpy as np

BASELINE = 10.0  # Distance between the two cameras in cm (this value is fixed after install)
FOCAL_LENGTH = 700  # Focal length in pixels (this can be determined by camera calibration)

# Define HSV color range for red laser pointer
laser_lower = np.array([0, 100, 100])
laser_upper = np.array([10, 255, 255])


def detect_laser_point(frame):
    """Detect the laser point in the given frame using color segmentation."""
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, laser_lower, laser_upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        if radius > 1:  # Filter out noise
            return int(x), int(y), radius
    return None


def calculate_distance(disparity):
    """Calculate the depth (Z) using the disparity."""
    if disparity == 0:  # Avoid division by zero
        return None
    distance = (FOCAL_LENGTH * BASELINE) / disparity
    return distance


def main():
    # Start video capture for both cameras
    cap1 = cv2.VideoCapture(0)  # First camera
    cap2 = cv2.VideoCapture(1)  # Second camera

    while True:
        # Capture frames from both cameras
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            print("Failed to capture video.")
            break

        # Detect laser point in both frames
        laser_point_cam1 = detect_laser_point(frame1)
        laser_point_cam2 = detect_laser_point(frame2)

        if laser_point_cam1 and laser_point_cam2:
            x1, y1, radius1 = laser_point_cam1
            x2, y2, radius2 = laser_point_cam2

            # Calculate disparity (difference in x-coordinates between the two images)
            disparity = abs(x1 - x2)

            # Calculate the distance of the laser point using the disparity
            distance = calculate_distance(disparity)

            if distance:
                # Draw the laser point and distance on both frames
                cv2.circle(frame1, (x1, y1), int(radius1), (0, 255, 0), 2)
                cv2.circle(frame2, (x2, y2), int(radius2), (0, 255, 0), 2)
                cv2.putText(frame1, f"Distance: {distance:.2f} cm", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame2, f"Distance: {distance:.2f} cm", (x2, y2 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display both camera feeds
        cv2.imshow('Camera 1', frame1)
        cv2.imshow('Camera 2', frame2)

        # Break the loop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and close windows
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()