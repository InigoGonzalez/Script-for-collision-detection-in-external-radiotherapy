# Script-for-detect-collision-in-external-radiotherapy-planning

The script has been adapted in order to be a boolean function:

    bool CheckCollision(ref PlanSetup planSetup)
    {
      bool collisionExists = false;
      MeshGeometry3D meshCouch = new MeshGeometry3D();
      MeshGeometry3D meshBody = new MeshGeometry3D();
      bool couchExists = false;

      foreach(Structure structure in planSetup.StructureSet.Structures)
      {
        if ( structure.Id == "CouchSurface" )
        {	
          meshCouch = structure.MeshGeometry;
          couchExists = true;
        }
        if ( structure.Id == "BODY" || structure.Id == "Externo" )
          meshBody = structure.MeshGeometry;			
      }

      foreach(Beam beam in planSetup.Beams)
      {
        if ( beam.IsSetupField)
          continue;
        Vector3D iso = new Vector3D(beam.IsocenterPosition.x, beam.IsocenterPosition.y, beam.IsocenterPosition.z);			
        double initialAngle = beam.ControlPoints[0].GantryAngle;
        double finalAngle = beam.ControlPoints[beam.ControlPoints.Count - 1].GantryAngle;
        double couchAngle = beam.ControlPoints[0].PatientSupportAngle;
        List<Point3D> points = CreateCollimator(initialAngle, finalAngle, couchAngle, 390, 380, 10);

        int extension = 0;
        if (couchAngle !=0)
          extension = 500;

        bool couchCollision = false;
        if(couchExists)
          couchCollision = Collision(meshCouch, points, iso, 15, extension, 25);			// tolerance = 2.5 cm

        bool patientCollision = Collision(meshBody, points, iso, 15, extension, 25);		// tolerance = 2.5 cm
        if (couchCollision)
          MessageBox.Show("Risk of collision with couch: Campo " + beam.Id.ToString() + ".\r\n");
        if (patientCollision)
          MessageBox.Show("Risk of collision with patient: Campo" + beam.Id.ToString() + ".\r\n");

        if (couchCollision || patientCollision)
        {
          collisionExists = true;
          Export(@"\\10.35.209.1\Varios\Scripts\ESAPI\collimator.txt", points);
          Export(@"\\10.35.209.1\Varios\Scripts\ESAPI\couch.txt", meshCouch, iso, 15, extension);
          Export(@"\\10.35.209.1\Varios\Scripts\ESAPI\body.txt", meshBody, iso, 15, extension);
          System.Diagnostics.Process.Start("cmd.exe", "/C \\\\10.35.209.1\\Varios\\Scripts\\PythonPortable\\App\\python.exe \\\\10.35.209.1\\Varios\\Scripts\\ESAPI\\PrintFile.py");
        }		
      }
      return collisionExists;
    }


Three extra functions are needed:

    public bool Collision(MeshGeometry3D mesh, List<Point3D> points, Vector3D iso, int reductionFactor = 1, double extension = 0, double tolerance = 25)
    {
      double minZ = mesh.Positions.Min(position => position.Z);
      for(int i = 0; i < mesh.Positions.Count; i += reductionFactor )
      {
        Point3D p1 = mesh.Positions[i];
        if (extension > 0 && p1.Z == minZ)
        {
          for(int e = 20; e <= extension; e += 20) // 2cm each
          {
            foreach(Point3D p2 in points) 
            {	
              if ( Math.Sqrt((p2.X - (p1.X - iso.X)) * (p2.X - (p1.X - iso.X)) + (p2.Y - (p1.Y - iso.Y)) * (p2.Y - (p1.Y - iso.Y)) + (p2.Z - (p1.Z - e - iso.Z)) * (p2.Z - (p1.Z - e - iso.Z))) < tolerance)
                return true;
            }
          }
        }

        foreach(Point3D p2 in points) 
        {	
          if ( Math.Sqrt((p2.X - (p1.X - iso.X)) * (p2.X - (p1.X - iso.X)) + (p2.Y - (p1.Y - iso.Y)) * (p2.Y - (p1.Y - iso.Y)) + (p2.Z - (p1.Z - iso.Z)) * (p2.Z - (p1.Z - iso.Z))) < tolerance)
            return true;
        }				
      }
      return false;
    }


    public void Export(string fileName, MeshGeometry3D mesh, Vector3D iso, int reductionFactor = 1, double extension = 0)
    {
      List<Point3D> meshPoints = new List<Point3D>();
      for(int i = 0; i < mesh.Positions.Count(); i += reductionFactor )
        meshPoints.Add(new Point3D(mesh.Positions[i].X - iso.X, mesh.Positions[i].Y - iso.Y, mesh.Positions[i].Z - iso.Z));

      StreamWriter outputFile = new StreamWriter(fileName);

      foreach(Point3D p in meshPoints)
        outputFile.WriteLine(p.X.ToString() + " " + p.Y.ToString() + " " + p.Z.ToString());

      if ( extension > 0 )
      {
        double minZ = meshPoints.Min(position => position.Z);
        foreach(Point3D p1 in meshPoints)
        {
          if(p1.Z < minZ + 10)
          {
            for(int e = 0; e <= extension; e += 50) // 5cm each
            {
              double z = p1.Z - e;
              outputFile.WriteLine(p1.X.ToString() + " " + p1.Y.ToString() + " " + z.ToString()); 
            }
          }
        }
      }				
      outputFile.Close();
      return;
    }
    
    
    // angles in degrees, distances in mm
    public List<Point3D> CreateCollimator(double startAngle, double finishAngle, double couchAngle, double clearance, double radius, double spacing = 10)
    {
      double ai = 0;
      double af = 0;
      if (startAngle  <= 180) ai = (180 - startAngle) * Math.PI/180.0;
      if (startAngle  >  180) ai = (540 - startAngle) * Math.PI/180.0;
      if (finishAngle <= 180) af = (180 - finishAngle)* Math.PI/180.0;
      if (finishAngle >  180) af = (540 - finishAngle)* Math.PI/180.0;
      double am = - couchAngle * Math.PI/180.0;

      List<Point3D> points = new List<Point3D>();

      if (ai > af) 
      { 		
        double aux = af;
        af = ai;
        ai = aux;
      }

      // Path
      for (double a = ai; a <= af; a += spacing / clearance)
      {
        for (double r = - radius; r <= radius; r += spacing)
          points.Add(new Point3D(clearance * Math.Sin(a) * Math.Cos(am) - r * Math.Sin(am), 
                                 clearance * Math.Cos(a), 
                                 clearance * Math.Sin(a) * Math.Sin(am) + r * Math.Cos(am)));		
      }	
        // Path extremes
      for (double r = spacing; r <= radius; r += spacing)
      {
        for (double b = 0; b <= Math.PI; b += spacing / r)
        {
          points.Add(new Point3D(clearance * Math.Sin(ai) * Math.Cos(am) - r * Math.Cos(ai) * Math.Sin(b) * Math.Cos(am) - r * Math.Cos(b) * Math.Sin(am), 
                                 clearance * Math.Cos(ai) + r * Math.Sin(ai) * Math.Sin(b), 
                                 clearance * Math.Sin(ai) * Math.Sin(am) - r * Math.Cos(ai) * Math.Sin(b) * Math.Sin(am) + r * Math.Cos(b) * Math.Cos(am)));
          points.Add(new Point3D(clearance * Math.Sin(af) * Math.Cos(am) + r * Math.Cos(af) * Math.Sin(b) * Math.Cos(am) - r * Math.Cos(b) * Math.Sin(am), 
                                 clearance * Math.Cos(af) - r * Math.Sin(af) * Math.Sin(b), 
                                 clearance * Math.Sin(af) * Math.Sin(am) + r * Math.Cos(af) * Math.Sin(b) * Math.Sin(am) + r * Math.Cos(b) * Math.Cos(am)));
        }				
      }	
      return points;
    }
