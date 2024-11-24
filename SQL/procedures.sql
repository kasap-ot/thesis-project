CREATE OR REPLACE PROCEDURE accept_student(
    student_id_p INT,
    offer_id_p INT
) AS $$
DECLARE
    waiting INT := 0;
    accepted INT := 1;
    rejected INT := 2;
BEGIN
    -- Accept the student for the offer, if he is waiting for an answer.
    UPDATE applications
    SET status = accepted
    WHERE student_id = student_id_p AND offer_id = offer_id_p AND status = waiting;

    -- Reject all other students for the same offer, if they are still waiting.
    UPDATE applications
    SET status = rejected
    WHERE student_id <> student_id_p AND offer_id = offer_id_p AND status = waiting;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE cancel_application(
    student_id_p INT,
    offer_id_p INT
) AS $$
DECLARE
    waiting INT := 0;
    accepted INT := 1;
    application_status INT;
BEGIN
    -- Check the status of the specified application
    SELECT status INTO application_status
    FROM applications
    WHERE student_id = student_id_p AND offer_id = offer_id_p;

    IF application_status = accepted THEN
        -- Remove the application and reset all other 
        -- applications for the same offer
        DELETE FROM applications
        WHERE student_id = student_id_p AND offer_id = offer_id_p;

        UPDATE applications
        SET status = waiting
        WHERE student_id <> student_id_p AND offer_id = offer_id_p;
    
    ELSIF application_status = waiting THEN
        -- Just remove the specified application.
        DELETE FROM applications
        WHERE student_id = student_id_p AND offer_id = offer_id_p;
    END IF;
END;
$$ LANGUAGE plpgsql;
