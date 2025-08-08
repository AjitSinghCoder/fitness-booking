from rest_framework.response import Response
from rest_framework import status

class CustomResponse:
    """
    Utility class for returning consistent API responses.
    """

    @staticmethod
    def list_response(data, message="Data fetched successfully"):
        return Response(
            {
                "status": "success",
                "message": message,
                "count": len(data) if isinstance(data, list) else None,
                "data": data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def single_item_response(data, message="Data fetched successfully"):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def create_response(data, message="Created successfully"):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data
            },
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def update_response(data=None, message="Updated successfully"):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def delete_response(message="Deleted successfully"):
        return Response(
            {
                "status": "success",
                "message": message
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def error_occurred_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "status": "error",
                "message": message,
                "errors": errors
            },
            status=status_code
        )

    @staticmethod
    def not_found_response(message="Not found"):
        return Response(
            {
                "status": "error",
                "message": message
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized_response(message="Unauthorized"):
        return Response(
            {
                "status": "error",
                "message": message
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def success_response(message="Action completed successfully"):
        return Response(
            {
                "status": "success",
                "message": message
            },
            status=status.HTTP_200_OK
        )
