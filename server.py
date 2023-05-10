from app import app
import controllers.user
import controllers.transaction
import controllers.report
import controllers.budget
import controllers.image_extractor

if __name__ == '__main__':
  app.run(threaded=True, host='0.0.0.0', port='5000')