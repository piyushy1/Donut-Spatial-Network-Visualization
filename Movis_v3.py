# Author: Piyush Yadav
# This functionality cretes a donut diagram of spatial networks

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from itertools import chain
from collections import Counter
import ast

# global dictionary to update the data
donut_dictionary = {}

# function to load the project
def load_project(project_path):
    project = QgsProject.instance()
    project.read(project_path)


# function to get all the layers
def get_all_layers():
    for layer in QgsProject.instance().mapLayers().values():
        print(layer.name())
    
# check the nodes direction by seeing in polygon
def check_nodes_direction(point, polygon_dict,node_label):
    
    for direction, polygon in polygon_dict.items():
        #a = QgsGeometry.asPoint(polygon)
#        a = polygon.asPolygon()
#        b = []
#        for i in range(len(a[0])):
#            #print(a[0][i])
#            b.append((a[0][i].x(),a[0][i].y()))
            
        if polygon.contains(point) == True:
            #print('True*****************', node_label[1])
            value = {'Direction': direction}
            donut_dictionary[node_label[1]] = value
            #print('Point present in direction', direction,donut_dictionary)
            
#        point_xy = (point.x(),point.y())
#        #print(b, point_xy)
#        
#        if point_xy in b:
#             print('OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK...',polygon, point, node_label[1])
#
#        else:
#            if node_label[1] == 'A':
#                print('False**********', polygon, point, node_label[1])

def identify_edges(edge_label_old, length):
    #print(edge_label_old)
    edge_label = [int(edge_label_old[i]) for i in range(len(edge_label_old))]
    if edge_label[1] in donut_dictionary.keys():
        value = donut_dictionary[edge_label[1]]
        if 'SourceEdge' in value.keys():
            new_val = value['SourceEdge']
            new_val.append(edge_label[1])
            value['SourceEdge'] = new_val
        else:
            value['SourceEdge'] = [edge_label[1]]
            
        if 'SourceLength' in value.keys():
            new_val1 = value['SourceLength']
            new_val1.append(length)
            value['SourceLength'] = new_val1
        else:
            value['SourceLength'] = [length]
        
    #print('************', edge_label[2])
    if edge_label[2] in donut_dictionary.keys():
        value = donut_dictionary[edge_label[2]]
        #print(value)
        if 'DestEdge' in value.keys():
            new_val = value['DestEdge']
            new_val.append(edge_label[2])
            value['DestEdge'] = new_val
        else:
            value['DestEdge'] = [edge_label[2]]

        if 'DestLength' in value.keys():
            new_val1 = value['DestLength']
            new_val1.append(length)
            value['DestLength'] = new_val1
        else:
            value['DestLength'] = [length]
        
    #print(donut_dictionary)

def get_attributes(feature):
    # fetch attributes
    attrs = feature.attributes()
    # attrs is a list. It contains all the attribute values of this feature
    return attrs
    
    
# get features of each layers
def get_features_of_layers(layer, request, polygon_dict):
    features = layer.getFeatures(request)
    for feature in features:
        # retrieve every feature with its geometry and attributes
        print("Feature ID: ", feature.id())
        # fetch geometry
        # show some information about the feature geometry
        geom = feature.geometry()
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geom.type() == QgsWkbTypes.PointGeometry:
            # the geometry type can be of single or multi type
            if geomSingleType:
                x = geom.asPoint()
                #print("Point: ", x)
                node_label = get_attributes(feature)
                print(node_label)
                check_nodes_direction(x, polygon_dict,node_label)
                                
            else:
                x = geom.asMultiPoint()
                print("MultiPoint: ", x)
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if geomSingleType:
                x = geom.asPolyline()
                #print("Line: ", x, "length: ", geom.length())
                edge_label = get_attributes(feature)
                identify_edges(edge_label, geom.length())
            else:
                x = geom.asMultiPolyline()
                print("MultiLine: ", x, "length: ", geom.length())
        elif geom.type() == QgsWkbTypes.PolygonGeometry:
            if geomSingleType:
                x = geom.asPolygon()
                print("Polygon: ", x, "Area: ", geom.area())
            else:
                x = geom.asMultiPolygon()
                print("MultiPolygon: ", x, "Area: ", geom.area())
        else:
            print("Unknown or invalid geometry")

def sortnodeedge_list_layer(layer):
    node_layer = []
    edge_layer =[]
    for i in range(len(layer)):
        if 'node'.casefold() in (layer[i].name()).casefold():
            node_layer.append(layer[i])
        if 'edge'.casefold() in (layer[i].name()).casefold():
            edge_layer.append(layer[i])
    
    layer_list = node_layer + edge_layer
    return layer_list
    

# function to get all the visible layers/active layers
def get_all_visible_layers_nodes_direction(polygon_dict):
    # function to select features from map extent
    extent = iface.mapCanvas().extent()
    request = QgsFeatureRequest()
    request.setFilterRect(extent)
    #layer = iface.activeLayer()
    # write a function to process first all node layers
    # then all edge layers
    # current fix put nodes and edges in the layer name in end
    layer1 = iface.mapCanvas().layers()
    final_layer = sortnodeedge_list_layer(layer1)
    for layer in final_layer:
        print(layer.name())
        get_features_of_layers(layer,request, polygon_dict)

# function to get bounding box of layer extent
def get_bouding_box_active_layer():
    layer = iface.activeLayer() # load the layer as you want
    ext = layer.extent()
    xmin = ext.xMinimum()
    xmax = ext.xMaximum()
    ymin = ext.yMinimum()
    ymax = ext.yMaximum()
    center = ext.center()
    coords = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)
    #print(coords, ext, ext.center())
    nort_west_point = (xmin,ymax)
    print(nort_west_point)

# function to get mid point
def mid_point(pt1, pt2):
    x = (pt1.x() + pt2.x())/2
    y = (pt1.y() + pt2.y())/2
    return QgsPointXY(x,y)

# function to create polygons from the list of coordinates
def create_polygon(coords, key, value_dict):
    polygon = QgsGeometry.fromPolygonXY( [[ QgsPointXY(pair[0], pair[1]) for pair in coords ]] )
    
    #visualize direction polygon
    create_vector_layer(polygon, 2)
    
    value_dict[key] = polygon
    #print(polygon)
    
def create_vector_layer(points, bool_val):
    # Specify the geometry type
    layer = QgsVectorLayer('Polygon?crs=epsg:4326', 'polygon' , 'memory')
    # Set the provider to accept the data source
    prov = layer.dataProvider()
    # Add a new feature and assign the geometry
    feat = QgsFeature()
    if bool_val == 1:
        feat.setGeometry(QgsGeometry.fromPolygonXY([points]))
    if bool_val == 2:
        feat.setGeometry(points)
    #feat.setGeometry(QgsGeometry.fromPolygonXY([polygon]))
    prov.addFeatures([feat])
     
    # Update extent of the layer
    layer.updateExtents()
     
    # Add the layer to the Layers panel
    QgsProject.instance().addMapLayers([layer])
    

# function to get bounding box of layer extent
def get_polygon_directons():
    #layer = iface.mapCanvas()
    layer = iface.activeLayer() # load the layer as you want
    ext = layer.extent()
    #print(ext)
    center = ext.center()
    x_center = ext.center().x()
    y_center = ext.center().y()
    xmin = ext.xMinimum()-1
    xmax = ext.xMaximum()+1
    ymin = ext.yMinimum()-1
    ymax = ext.yMaximum()+1
#    test_point = QgsPointXY(-6.23742530039480858, 53.37665009353574419)
#    print('Test', ext.contains(test_point))
    
    # arrange the points in cyclic order starting from top left
    north_west_point = QgsPointXY(xmin,ymax)
    north_point = QgsPointXY(x_center,ymax)
    north_east_point = QgsPointXY(xmax,ymax)
    east_point = QgsPointXY(xmax,y_center)
    south_east_point = QgsPointXY(xmax, ymin)
    south_point = QgsPointXY(x_center,ymin)
    south_west_point = QgsPointXY(xmin,ymin)
    west_point = QgsPointXY(xmin,y_center)
    bb_points = [north_west_point,north_point,north_east_point,east_point,south_east_point,south_point,south_west_point,west_point]
    #print('Bounding BoX ',bb_points)
    # create bounding box
    #create_vector_layer(bb_points, 1)
    
    
    # get the mid points from clockwise top left
    north_west_north_midpoint = mid_point(north_west_point,north_point)
    north_east_north_midpoint = mid_point(north_point,north_east_point)
    north_east_east_midpoint = mid_point(north_east_point,east_point)
    south_east_east_midpoint = mid_point(east_point,south_east_point)
    south_east_south_midpoint = mid_point(south_east_point,south_point)
    south_west_south_midpoint = mid_point(south_point, south_west_point)
    south_west_west_midpoint = mid_point(south_west_point,west_point)
    north_west_west_midpoint = mid_point(west_point, north_west_point)
    
    # create direction polygons from the above points
    direction_polygon_dict = {}
    north_west_polygon = create_polygon([north_west_west_midpoint,north_west_point,north_west_north_midpoint, center],'north_west',direction_polygon_dict )
    north_polygon = create_polygon([north_west_north_midpoint, north_point, north_east_north_midpoint, center], 'north', direction_polygon_dict)
    north_east_polygon = create_polygon([north_east_north_midpoint, north_east_point, north_east_east_midpoint, center],'north_east', direction_polygon_dict)
    east_polygon = create_polygon([north_east_east_midpoint,east_point, south_east_east_midpoint, center], 'east', direction_polygon_dict)
    south_east_polygon = create_polygon([south_east_east_midpoint, south_east_point, south_east_south_midpoint, center], 'south_east', direction_polygon_dict)
    south_polygon = create_polygon([south_east_south_midpoint, south_point, south_west_south_midpoint, center],'south', direction_polygon_dict)
    south_west_polygon = create_polygon([south_west_south_midpoint, south_west_point, south_west_west_midpoint, center], 'south_west', direction_polygon_dict)
    west_polygon = create_polygon([south_west_west_midpoint, west_point, north_west_west_midpoint, center],'west', direction_polygon_dict)
    #print(direction_polygon_dict)
    return direction_polygon_dict

def sanitize_labels(labels):
    final_labels = []
    final_rearranged_labels =[]
    for i in range(len(labels)):
        label = ast.literal_eval(labels[i])
        if isinstance(label[0], dict):
            for key, value in label[0].items():
                if isinstance(value, list):
                    label[0][key] = sum(value)
            final_labels.append(str(label))
            # rearrange as near, medium, far
            rearrange_label =[]
            for key in sorted(label[0]):
                rearrange_label.append("%s: %s" % (key, label[0][key]))
                
            rearrange_label.reverse()
            final_rearranged_labels.append(str(rearrange_label))
        else:
            final_labels.append(labels[i])
            final_rearranged_labels.append(labels[i])
    
    return final_labels,final_rearranged_labels

def map_color_code(data,normalise_color_code):
    #colors = ['#EEFFCC', '#CCFF66', '#AAFF00', '#88CC00', '#446600'] #green
    colors = ['#EDEDED', '#D3D3D3', '#ABABAB', '#4D4D4D', '#171717']
    if data in normalise_color_code.keys():
        value = normalise_color_code[data]
        if value <= 0.20:
            return colors[0]
        if 0.21 <= value <= 0.40:
            return colors[1]
        if 0.41 <= value <= 0.60:
            return colors[2]
        if 0.61 <= value <= 0.80:
            return colors[3]
        if 0.81 <= value <= 1.0:
            return colors[4]    
        
def generate_color_band(labels):
    # remove string
    new_labels = [ast.literal_eval(labels[i]) for i in range(len(labels))]
    all_data = []
    far = []
    near = []
    medium = []
    
    # get all edges
    for i in range(len(new_labels)):
        if isinstance(new_labels[i][0], dict):
            if 'Far' in new_labels[i][0].keys():
                all_data.append(new_labels[i][0]['Far'])
            if 'Near' in new_labels[i][0].keys():
                all_data.append(new_labels[i][0]['Near'])
            if 'Medium' in new_labels[i][0].keys():
                all_data.append(new_labels[i][0]['Medium'])
        else:
            print('not dict')
    
    # normalise length
    normalise_len = [float(i)/max(all_data) for i in all_data]
    normalise_color_code = dict(zip(all_data,normalise_len))
    
    # map the color code
    for i in range(len(new_labels)):
        if isinstance(new_labels[i][0], dict):
            if 'Far' in new_labels[i][0].keys():
                far.append(map_color_code(new_labels[i][0]['Far'],normalise_color_code))
            else:
                far.append('#FFFFFF')
            if 'Near' in new_labels[i][0].keys():
                near.append(map_color_code(new_labels[i][0]['Near'],normalise_color_code))
            else:
                near.append('#FFFFFF')
            if 'Medium' in new_labels[i][0].keys():
                medium.append(map_color_code(new_labels[i][0]['Medium'],normalise_color_code))
            else:
                medium.append('#FFFFFF')
                
        else:
            far.append('#FFFFFF')
            near.append('#FFFFFF')
            medium.append('#FFFFFF')
    
    print('************', far, near, medium)
    return far, medium, near
    
                
def create_donut_chart():
    fig, ax = plt.subplots()
    size = 0.4
    vals = np.array([[150., 150.], [150., 150.], [150., 150.], [150., 150.]])
    #print(vals)
    cmap = plt.get_cmap("tab20c")
    #print(cmap)
    #outer_colors = cmap(np.arange(3)*4)
    inner_colors = cmap(np.array([1, 2, 5, 6, 9, 10]))
    #color_set = ('.00', '.25', '.50', '.75')
    # create color list
    colors = ['#EEFFCC', '#CCFF66', '#AAFF00', '#88CC00', '#446600']
    # create labels
    labels = get_donut_plot_labels()
    # sanitize
    recipe, rearranged_recipe = sanitize_labels(labels)
    
    print(recipe)
    
    # create color list for all pies
    inner_colors1,inner_colors2,inner_colors3 = generate_color_band(recipe)

    print(vals.sum(axis=1), vals.flatten())

    wedges, texts = ax.pie(vals.flatten()*4, radius=1.5, colors=inner_colors1,
           wedgeprops=dict(width=size, edgecolor= 'w',linewidth=0.1), startangle = -155)

    ax.pie(vals.flatten(), radius=1.5-size, colors=inner_colors2,
           wedgeprops=dict(width=size, edgecolor= 'w', linewidth=0),startangle = -155)

    ax.pie(vals.flatten()*2, radius=1.5-0.8, colors=inner_colors3,
           wedgeprops=dict(width=size, edgecolor= 'w',linewidth=0), startangle = -155)

    # get the information from donut dictionary
    num_nodes = len(donut_dictionary)
    
    
#    recipe = ["Total 9\n 2-Far\n 3-Medium",
#              "South",
#              "South East",
#              "East",
#              "North East",
#              "North",
#              "North West",
#              "West"]
    
#    labels = get_donut_plot_labels()
#    # sanitize
#    recipe = sanitize_labels(labels)
#    
#    print(recipe)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        if "['No Nodes Present']" not in rearranged_recipe[i]:
            ax.annotate(rearranged_recipe[i], xy=(x, y), xytext=(1.5*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment, **kw)


    #ax.set(aspect="equal", title='Pie plot with `ax.pie`')
    ax.set(aspect="equal")
    #ax.legend(colors)
    plt.title(str(num_nodes), x = 0.5, y = 0.47)
    img1 = mpimg.imread("C:/PhD Docs/Movis/QGIS_Dataset/compass1.png")
    img2 = mpimg.imread("C:/PhD Docs/Movis/QGIS_Dataset/legend.png")
    plt.figimage(img1, 1500, 280, zorder=1, alpha=1)
    plt.figimage(img2, 1450, 205, zorder=1, alpha=1)
    plt.savefig('C:/PhD Docs/Movis/Donut_Chart.jpg', dpi=None)
    load_raster_map('C:/PhD Docs/Movis/Donut_Chart.jpg')
    plt.show()
    
        
#def create_arrow_chart():
    

# normalising destination length... same can be done for soure
def dest_normalise_length():
    leng = []
    for key, value in donut_dictionary.items():
        if 'DestLength' in value.keys():
            leng.append(value['DestLength'])

    # flatten the list
    newlist = list(chain(*leng))
    #print('************', leng)
    #print('************', newlist)
    # normalise list with maximum value
    normalise_len = [float(i)/max(newlist) for i in newlist]
    #print('************', normalise_len)
    # update near, medium, far
    # current threshoild this can be changed or complex stats can be used
    # near: 0-0.35, medium: 3.6-6 and far > 6
    for i in range(len(newlist)):
        for key, value in donut_dictionary.items():
            if 'DestLength' in value.keys():
                if newlist[i] in value['DestLength']:
                    if 'DestNormaliseLen' in value.keys():
                        new_val = value['DestNormaliseLen']
                        new_val.append(normalise_len[i])
                        value['DestNormaliseLen'] = new_val
                    else: 
                        value['DestNormaliseLen'] = [normalise_len[i]]
                    
                    if 'DestRange' in value.keys():
                        val1 = value['DestRange']
                        if normalise_len[i] <= 0.35:
                           val1.append('Near')
                        
                        if 0.36 <= normalise_len[i] <= 0.60:
                            val1.append('Medium')
                        if normalise_len[i] > 0.60:
                            val1.append('Far')
                           
                    else: 
                        if normalise_len[i] <= 0.35:
                            value['DestRange'] = ['Near']
                        if 0.36 <= normalise_len[i] <= 0.60:
                            value['DestRange'] = ['Medium']
                        if normalise_len[i] > 0.60:
                            value['DestRange'] = ['Far']

# normalising destination length... same can be done for soure
def source_normalise_length():
    leng = []
    for key, value in donut_dictionary.items():
        if 'SourceLength' in value.keys():
            leng.append(value['SourceLength'])

    # flatten the list
    newlist = list(chain(*leng))
    #print('************', leng)
    #print('************', newlist)
    # normalise list with maximum value
    normalise_len = [float(i)/max(newlist) for i in newlist]
    #print('************', normalise_len)
    # update near, medium, far
    # current threshoild this can be changed or complex stats can be used
    # near: 0-0.35, medium: 3.6-6 and far > 6
    for i in range(len(newlist)):
        for key, value in donut_dictionary.items():
            if 'SourceLength' in value.keys():
                if newlist[i] in value['SourceLength']:
                    if 'SourceNormaliseLen' in value.keys():
                        new_val = value['SourceNormaliseLen']
                        new_val.append(normalise_len[i])
                        value['SourceNormaliseLen'] = new_val
                    else: 
                        value['SourceNormaliseLen'] = [normalise_len[i]]
                    
                    if 'SourceRange' in value.keys():
                        val1 = value['SourceRange']
                        if normalise_len[i] <= 0.35:
                           val1.append('Near')
                        
                        if 0.36 <= normalise_len[i] <= 0.60:
                            val1.append('Medium')
                        if normalise_len[i] > 0.60:
                            val1.append('Far')
                           
                    else: 
                        if normalise_len[i] <= 0.35:
                            value['SourceRange'] = ['Near']
                        if 0.36 <= normalise_len[i] <= 0.60:
                            value['SourceRange'] = ['Medium']
                        if normalise_len[i] > 0.60:
                            value['SourceRange'] = ['Far']

def load_raster_map(raster):
    # Check if string is provided

    fileInfo = QFileInfo(raster)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    layer = QgsRasterLayer(path, baseName)
    QgsProject.instance().addMapLayer(layer)

    if layer.isValid() is True:
        print ("Layer was loaded successfully!")

    else:
        print ("Unable to read basename and file path - Your string is probably invalid")

def get_donut_plot_labels():
    final_labels =[]
    labels1 =["south_west","south","south_east","east","north_east","north","north_west","west"]
    
    for i in range(len(labels1)):
        labels = []
        for item_val in donut_dictionary.values():
            if item_val['Direction'] == labels1[i]:
                if 'DestRange' in item_val:
                    dest_list = item_val['DestRange']
                    counter = Counter(dest_list)
                    labels.append(dict(counter))
                else:
                    labels.append('No Destination Edges Present')

                if 'SourceRange' in item_val:
                    dest_list = item_val['SourceRange']
                    counter = Counter(dest_list)
                    labels.append(dict(counter))
                else:
                    labels.append('No Destination Edges Present')
                    
        #print(labels)
        final_labels.append(labels)
    
    for i in range(len(final_labels)):
        if len(final_labels[i]) == 0:
            final_labels[i] = ['No Nodes Present']
            
        if len(final_labels[i]) > 1:
            if 'No Destination Edges Present' in final_labels[i]:
                final_labels[i] = [value for value in final_labels[i] if value != 'No Destination Edges Present']
                #list(filter(('No Destination Edges Present').__ne__, final_labels[i]))
                #final_labels[i].remove('No Destination Edges Present')
                
            if 'No Destination Edges Present' not in final_labels[i]: 
                print(final_labels[i], )
                bar = {k: [d.get(k) for d in final_labels[i]]
                for k in set().union(*final_labels[i])
                }
                for key, values in bar.items():
                    bar[key] = list(filter(None.__ne__, values))
                final_labels[i] = [bar]
            
    for i in range(len(final_labels)):
        final_labels[i] = str(final_labels[i])
        
    #print(final_labels)
    
    return final_labels
    

# load the qgis project
#load_project('C:/PhD Docs/Movis/QGIS_Dataset/SpatialSocialNetworks.gpkg')

# get bb
polygon_dict = get_polygon_directons()

# get all visible layers
get_all_visible_layers_nodes_direction(polygon_dict)

# normalise the length and update the donut dictionary
dest_normalise_length()

# normalise the length and update the donut dictionary
source_normalise_length()

# create donut chart
create_donut_chart()


